import requests
import json
import random
import jwt
from datetime import timedelta
from .serializers import RegisterSerializer, LoginSerializer, ContactSerializer, CustomAuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from geopy.geocoders import Nominatim
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import IntegrityError
from .models import OTP, Users, Contacts, Emergency
from .tasks import send_sms_task, send_email_task


class UserRegistrationView(APIView):
    # permission_classes = [IsAuthenticated]

    # @method_decorator(ratelimit(key='ip', rate='30/d', method='POST'))
    def post(self, request):
            
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        OTP.send_otp_email(user.email)   

        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_201_CREATED)

class VerifyPhoneNumber(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Check if the phone number already exists
            if Users.objects.filter(phone_number=phone_number).exclude(email=user.email).exists():
                return Response(
                    {"error": "This phone number is already in use by another user."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update the phone number for the authenticated user
            user.phone_number = phone_number
            user.is_phone_verified = False  # Reset phone verification if applicable
            user.save()

            # Send OTP to the phone number
            OTP.send_sms(phone_number)
            return Response({'message': 'OTP sent to phone number successfully.'}, status=status.HTTP_200_OK)

        except IntegrityError:
            return Response(
                {"error": "Failed to update phone number due to a database constraint."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerifyPhoneNumberOTP(APIView):
    def post(self, request):
        
        phone_number =  request.data.get('phone_number')
        otp =  request.data.get('otp')
        
        user = Users.objects.filter(email=request.user).first()
        print('use', user)
        if user:
            success = OTP.verify_otp(phone_number, otp)
            if success:
                # phone_num = Users.objects.update_or_create(phone_number=phone_number)
                # phone_num.save()
                user.is_phone_verified = True
                user.save()
                tokens = user.tokens()
                # refresh = tokens['refresh']
                # access = tokens['access']
                return Response({'message': 'Phone number verified successfully',
                                'tokens' : tokens, 
                                #  'access': access, 
                                # 'refresh' : refresh,
                                'is_phone_verified' : user.is_phone_verified,
                                'first_name':user.first_name,
                                'last_name':user.last_name,
                                 }, status=status.HTTP_200_OK)
            return 
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            
class VerifyEmailAddress(APIView):
    def post(self, request):
        
        email_address =  request.data.get('email')
        otp =  request.data.get('otp')
        
        user = Users.objects.filter(email=email_address).first()
        
        if user:
            success = OTP.verify_otp(email_address, otp)
            if success:
                user.is_verified = True
                user.save()
                tokens = user.tokens()
                return Response({'message': 'Email Address verified successfully. Proceed to verify phone number',
                                 'tokens': tokens, 
                                 }, status=status.HTTP_200_OK)
            return 
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            
class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomAuthenticationFailed as e:
            return Response(e.detail, status=status.HTTP_307_TEMPORARY_REDIRECT)


class GenerateOTP(APIView):
    def post(self, request):
        item = request.data.get('email')
        if '@' in item:
            user = Users.objects.filter(email=item).first()
            if user:  
                OTP.send_otp_email(user.email)
                return Response({'message': 'OTP has been sent to your email'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = Users.objects.filter(phone_number=item).first()
            if user:  
                OTP.send_sms(user.phone_number)
                return Response({'message': 'OTP has been sent to your phone'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except (RefreshToken.DoesNotExist, ValidationError):
                return Response({'Failed': 'The operation is invalid'},status=status.HTTP_404_NOT_FOUND)
                  # Ignore potential errors if token is invalid or blacklisted already
        return Response(status=status.HTTP_204_NO_CONTENT)

class CreateRelation(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        subscription_limits ={
            'free': 5,
            'pro': 10,
            'advance': 15
        }
        
        subscription_level = user.get_subscription_level()
        contact_count = Contacts.objects.filter(created_by=user).count()
        max_contacts = subscription_limits.get(subscription_level, 5)
        
        if contact_count >= max_contacts:
            return Response(f"Contact limit reached for {subscription_level} subscription",
                            status=status.HTTP_403_FORBIDDEN
                            )
        try:
            contact_user = Users.objects.get(phone_number=request.user.phone_number)
            createdby = Users.objects.get(email=request.user)

        except Users.DoesNotExist:
            contact_user = None
            
        contact_data = {
            'created_by': createdby,
            'first_name' : request.data.get('first_name'),
            'last_name' : request.data.get('last_name'),
            'phone_number' : request.data.get('phone_number'),
            'email_address' : request.data.get('email_address'),
            'relation' : request.data.get('relation'),
            'contact_user': contact_user
        }    
        
        createrela = Contacts.objects.create(**contact_data)     
        createrela.save()
        
        token = RefreshToken.for_user(user).access_token
        token.set_exp(lifetime=timedelta(days=1))
        
        message = (
            f'From: Help OO Help,\n\n'
            f'Subject: Emergency Alert Confirmation \n\n'
            f"Dear {request.data.get('first_name')} {request.data.get('last_name')}, \n"
            f"Your {(request.data.get('relation')).lower()}, {user.get_fullname()}, has nominated you, that you should \n"
            f"be contacted in case of emergency.\n"
            f"Kindly click on the link below to ACCEPT or REJECT the nomination.\n"
            f"http://localhost:3000/guestInvite/accept/?token={token}&contact_id={createrela.id}"            
        )
        try:   
            rand = str(random.randint(10, 999))       
            post_data = {
                    "senderid": settings.WIGAL_SENDER_ID,
                    "destinations": [
                        {
                        "destination": request.data.get('phone_number'),
                        "msgid": f"MGS{rand}"
                        }
                    ],
                    "message": message,
                    "smstype": "text"
                    }
            print('post', post_data)
            send_sms_task(post_data)
            # send_email_task(post_data)
        except Exception as e:
            print(f"Failed to send SMS to {contact_data['phone_number']}: {str(e)}")
                
        
        return Response({'message':'Contact created successfully'}, status=status.HTTP_201_CREATED)

class ContactDetails(APIView):
    permission_classes = [AllowAny]

    def get(self, request, contact_id):
        try:
            contact = Contacts.objects.get(id=contact_id)
            return Response({
                'contact_first_name': contact.first_name,
                'contact_last_name': contact.last_name,
                'sender_name': contact.created_by.get_fullname()
            }, status=status.HTTP_200_OK)
        except Contacts.DoesNotExist:
            return Response({'error': 'Contact not found.'}, status=status.HTTP_404_NOT_FOUND)

class UpdateRelationStatus(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            contact_id = request.data.get('contact_id')
            action = request.data.get('action')
            token = request.data.get('token')
            
            if not contact_id or not action:
                return Response(
                    {"error": "Both 'contact_id' and 'action' are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if action not in ['approved', 'rejected']:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

            set_key = str(settings.SECRET_KEY)
            
            try:
                jwt.decode(token, set_key, algorithms=["HS256"])
            
            except jwt.ExpiredSignatureError as identifier:
                return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
            
            except jwt.exceptions.DecodeError as identifier:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)    # Redirect to frontend login page
            
            try:
                contact = Contacts.objects.get(id=contact_id)
                contact.status = action
                contact.save()
                
                message = (
                f"Dear {contact.first_name} {contact.last_name},\n\n"
                f"You have successfully {'accepted' if action == 'approved' else 'rejected'} "
                f"the nomination by {contact.created_by.get_full_name}.\n"
            )
                try:
            
                    post_data= {'recipient': contact.phone_number, 'message': message}
                    headers = {
                    'Content-Type': 'application/json',
                    'API-KEY': settings.WIGAL_KEY,
                    'USERNAME': 'osaheneBlackmore'
                    }
                    print('post', post_data)
                    response = requests.post('https://frogapi.wigal.com.gh/api/v3/sms/send', headers=headers, data=json.dumps(post_data))
                    print(response.json())
                except Exception as e:
                    print(f"Failed to send SMS to {contact.phone_number}: {str(e)}")

                return Response(
                    {"message": f"Status updated to {action} successfully"},
                    status=status.HTTP_200_OK
                )
            except Contacts.DoesNotExist:
                return Response(
                    {"error": "Contact not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
           
        except Contacts.DoesNotExist:
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserContactsList(ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = ContactSerializer
    
    def get_queryset(self):
        return Contacts.objects.filter(created_by= self.request.user)
    
class UpdateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_subscription = request.data.get('subscription_level')

        if new_subscription not in ['free', 'pro', 'advance']:
            return Response(
                {"error": "Invalid subscription level"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.subscription_level = new_subscription
        user.save()

        return Response(
            {"message": f"Subscription updated to {new_subscription.capitalize()}."},
            status=status.HTTP_200_OK
        )
 
class DependantsListView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user        
        contacts = Contacts.objects.filter(email_address=user).first()
        
        if not contacts:
            return Response({'message': 'No contacts found'}, status=status.HTTP_404_NOT_FOUND)
        
        contacts_data = []
        
        for contact in contacts:
            contact_info = {
                'created_by': {
                    'first_name': contact.created_by.first_name,
                    'last_name': contact.created_by.last_name,
                    'email': contact.created_by.email,
                    'phone_number': contact.created_by.phone_number 
                },
                'id': contact.pk,
                'relation': contact.relation,
                'status': contact.status,
            }
            contacts_data.append(contact_info)
           
        if len(contacts_data) < 1:
            return Response({'message': 'Zero contacts found'}, status=status.HTTP_200_OK)
        return Response({'dependant_list': contacts_data}, status=status.HTTP_200_OK)
    
class ApproveDependantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        key = request.data
        try:
            contact = Contacts.objects.get(pk=key)
            contact.status = 'approved'
            contact.save()
            return Response({"message": "Contact approved"}, status=status.HTTP_200_OK)
        except Contacts.DoesNotExist:
            return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)

class RejectDependantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        key = request.data
        try:
            contact = Contacts.objects.get(pk=key)
            contact.status = 'rejected'
            contact.save()
            return Response({"message": "Contact rejected"}, status=status.HTTP_200_OK)
        except Contacts.DoesNotExist:
            return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)

class DeleteContactView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        contact = get_object_or_404(Contacts, pk=request.data.get('pk'), created_by=request.user)
        contact.delete()
        return Response({'message': 'Contact deleted successfully'}, status=status.HTTP_200_OK)
    
class UpdateContactView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        contact = get_object_or_404(Contacts, pk=request.data.get('pk'), created_by=request.user)
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Contact updated successfully'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmergencyActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        location = request.data.get('location')
        action = request.data.get('alertType')

        # Ensure necessary fields are provided
        if not location or not action:
            return Response(
                {"error": "Location and alertType are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Decode the location
        try:
            geolocator = Nominatim(user_agent="emergency_action_service")
            location_info = geolocator.reverse(
                query=(location['latitude'], location['longitude']),
                exactly_one=True
            ).raw['address']
            
            country = location_info.get('country', '')
            region = location_info.get('state', '')
            city = location_info.get('city', '')
            town = location_info.get('town', '')
            locality = location_info.get('suburb', '')
        except Exception as e:
            return Response(
                {"error": f"Failed to decode location: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Get user contacts
        contacts = Contacts.objects.filter(created_by=user, status='approved')
        if not contacts.exists():
            return Response(
                {"error": "No approved contacts found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Prepare personalized messages
        sms_payloads = []
        email_messages = []

        for index, contact in enumerate(contacts):
            message = (
                f"{action} Alert,\n\n"
                f"Hello {contact.first_name} {contact.last_name},\n\n"
                f"Your {contact.relation.lower()}, {user.get_fullname()}, has triggered an emergency {action.lower()} alert. "
                f"They are at {locality}, {town}, {city}, {region}, {country}.\n\n"
                f"View their location here:\n"
                f"https://www.openstreetmap.org/?mlat={location['latitude']}&mlon={location['longitude']}&zoom=15\n\n"
                "Please respond immediately.\n\nThank you."
            )

            # Add to SMS payload
            sms_payloads.append({
                "destination": contact.phone_number,
                "msgid": f"MSG_{index}",
                "message": message
            })

            # Add to email messages
            email_messages.append((
                f"{action} Alert",
                message,
                settings.DEFAULT_FROM_EMAIL,
                [contact.email_address]
            ))

        # Send SMS asynchronously
        sms_request_data = {
            "senderid": settings.WIGAL_SENDER_ID,
            "destinations": sms_payloads,
            "smstype": "text"
        }
        
        send_sms_task.delay(sms_request_data)

        # Send emails in bulk
        try:
            send_email_task.delay(email_messages)
        except Exception as e:
            print(f"Failed to send some emails: {str(e)}")

        # Save emergency action to the database
        try:
            Emergency.objects.create(
                created_by=user,
                action=action,
                location={"latitude": location['latitude'], "longitude": location['longitude']},
                country=country,
                region=region,
                city=city,
                town=town,
                locality=locality,
                mission_status="success",
            )
            return Response(
                {"message": "Emergency action successfully logged."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to log emergency action: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class USSDHandlerView(APIView):
    def post(self, request):
        session_id = request.data.get("sessionId")
        phone_number = request.data.get("phoneNumber")
        text = request.data.get("text", "")  # User's input
        
        # Parse text to determine USSD menu navigation
        inputs = text.split("*")
        user = Users.objects.filter(phone_number=phone_number).first()
        
        if text == "":
            # Initial menu
            response = "Welcome to the Emergency Service\n"
            response += "1. Register\n"
            response += "2. Trigger Emergency Alert\n"
            response += "3. View Registered Contacts"
        
        elif inputs[0] == "1":
            # Registration flow
            if len(inputs) == 1:
                response = "CON Enter your first name:"
            elif len(inputs) == 2:
                response = "CON Enter your last name:"
            elif len(inputs) == 3:
                response = "CON Enter your email address:"
            elif len(inputs) == 4:
                # Save user registration
                first_name, last_name, email = inputs[1], inputs[2], inputs[3]
                user, created = Users.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={"first_name": first_name, "last_name": last_name, "email": email}
                )
                if created:
                    response = "END Registration successful!"
                else:
                    response = "END You are already registered."
        
        elif inputs[0] == "2":
            # Trigger Emergency Alert Flow
            if len(inputs) == 1:
                # Emergency type selection
                response = "CON Select emergency type:\n"
                response += "1. Fire Outbreak\n"
                response += "2. Health Crisis\n"
                response += "3. Robbery Attack\n"
                response += "4. Violence Alert\n"
                response += "5. Flood Alert\n"
                response += "6. Call Emergency"
            elif len(inputs) == 2:
                # Prompt for location after emergency type selection
                response = "CON Enter your location:"
            elif len(inputs) == 3:
                # Trigger emergency and notify contacts
                try:
                    action_type = {
                        "1": "Fire Outbreak",
                        "2": "Health Crisis",
                        "3": "Robbery Attack",
                        "4": "Violence Alert",
                        "5": "Flood Alert",
                        "6": "Call Emergency",
                    }.get(inputs[1], "Unknown Emergency")
                    
                    location = inputs[2]
                    
                    # Notify contacts
                    contacts = Contacts.objects.filter(created_by=user, status="approved")
                    for contact in contacts:
                        # Prepare message details
                        message = (
                            f"{action_type} Alert,\n\n"
                            f"Hello {contact.first_name} {contact.last_name},\n\n"
                            f"Your {(contact.relation).lower()}, {user.get_fullname()} has triggered an emergency {(action_type).lower()} alert. "
                            f"They are at {location}.\n\n"
                            "Please respond as soon as possible.\n\nThank you."
                        )
                        
                        # Send SMS
                        try:
                            post_data = {"recipient": contact.phone_number, "message": message}
                            headers = {
                                "Content-Type": "application/json",
                                "API-KEY": settings.WIGAL_KEY,
                                "USERNAME": "osaheneBlackmore",
                            }
                            requests.post(
                    
                                "https://frogapi.wigal.com.gh/api/v3/sms/send",
                                headers=headers,
                                data=json.dumps(post_data),
                            )
                        except Exception as e:
                            print(f"Failed to send SMS to {contact.phone_number}: {str(e)}")
                        
                        # Send Email
                        try:
                            send_mail(
                                f"{action_type} Alert",
                                message,
                                settings.DEFAULT_FROM_EMAIL,
                                [contact.email_address],
                                fail_silently=False,
                            )
                        except Exception as e:
                            print(f"Failed to send email to {contact.email_address}: {str(e)}")
                    
                    # Save emergency to the database
                    Emergency.objects.create(
                        created_by=user,
                        action=action_type,
                        location_context=location,
                        usage_type="USSD",
                        mission_status="success",
                    )
                    response = "END Emergency alert triggered successfully!"
                except Exception as e:
                    response = "END Failed to trigger emergency alert. Please try again."

        elif inputs[0] == "3":
            # View registered contacts
            if len(inputs) == 1:
                contacts = Contacts.objects.filter(created_by=user)
                if contacts.exists():
                    response = "CON Your contacts:\n"
                    for i, contact in enumerate(contacts, 1):
                        response += f"{i}. {contact.first_name} {contact.last_name} ({contact.status})\n"
                else:
                    response = "END No contacts found. Add contacts to your profile."
            else:
                response = "END Invalid option selected."

        else:
            response = "END Invalid option selected."
        
        return Response(response, status=status.HTTP_200_OK)
