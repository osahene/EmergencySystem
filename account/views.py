from .serializers import RegisterSerializer, LoginSerializer, ContactSerializer, ContactStatusSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from geopy.geocoders import Nominatim
from rest_framework.permissions import IsAuthenticated
from .models import OTP, Users, Contacts, Emergency



class UserRegistrationView(APIView):
    # permission_classes = [IsAuthenticated]

    # @method_decorator(ratelimit(key='ip', rate='30/d', method='POST'))
    def post(self, request):
            
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        OTP.send_sms(user.phone_number)   

        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_201_CREATED)

class VerifyPhoneNumber(APIView):
    def post(self, request):
        
        phone_number =  request.data.get('phoneNumber')
        otp =  request.data.get('otp')
        
        user = Users.objects.filter(phone_number=phone_number).first()
        
        if user:
            success = OTP.verify_otp(phone_number, otp)
            if success:
                user.is_phone_verified = True
                user.save()
                tokens = user.tokens()
                refresh = tokens['refresh']
                access = tokens['access']
                return Response({'message': 'Phone number verified successfully',
                                 'access': access, 
                                'refresh' : refresh, 
                                'first_name':user.first_name,
                                'last_name':user.last_name,
                                 }, status=status.HTTP_200_OK)
            return 
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenerateOTP(APIView):
    def post(self, request):
        item = request.data.get('phoneNumber')
        if '@' in item:
            user = Users.objects.filter(email_address=item).first()
            if user:  
                OTP.send_otp_email(user.email_address)
                return Response({'message': 'OTP has been sent to your email'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = Users.objects.filter(phone_number=item).first()
            if user:  
                OTP.send_sms(user.phone_number, 'Your one-time password is')
                return Response({'message': 'OTP has been sent to your phone'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)


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
        
        return Response('Contact created successfully', status=status.HTTP_201_CREATED)
    
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
 
# @method_decorator(ensure_csrf_cookie, name='dispatch')
class DependantsListView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_phone_number = request.query_params.get('phone_number', None)
        
        if not user_phone_number:
            return Response({"error" : "invalid request"}, status=status.HTTP_403_FORBIDDEN)
        
        contacts = Contacts.objects.filter(phone_number=user_phone_number)
        
        if not contacts.exists():
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
            return Response({'message': 'No contacts found'}, status=status.HTTP_200_OK)
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
        print('del', request.data)
        contact = get_object_or_404(Contacts, pk=request.data.get('pk'), created_by=request.user)
        contact.delete()
        return Response({'message': 'Contact deleted successfully'}, status=status.HTTP_200_OK)
    
class UpdateContactView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        contact = get_object_or_404(Contacts, pk=request.data.get('pk'), created_by=request.user)
        serializer = ContactSerializer(contact, data=request.data)
        print('data',request.data)
        print('ser',serializer)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Contact updated successfully'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmergencyActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        location = request.data.get('location')  # Location coordinates (latitude, longitude)
        action = request.data.get('action_type')

        # Ensure necessary fields are provided
        if not location or not action:
            return Response(
                {"error": "Location and action_type are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Decode the location coordinates using OpenStreetMap (Geopy or OpenStreet API)
        try:
            geolocator = Nominatim(user_agent="emergency_action_service")
            location_info = geolocator.reverse(location, exactly_one=True).raw['address']

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

        # Fetch contacts related to the user
        contacts = Contacts.objects.filter(created_by=user, status='approved')
        if not contacts.exists():
            return Response(
                {"error": "No approved contacts found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Prepare and broadcast notifications for a fire action
        if action.lower() == "fire":
            for contact in contacts:
                # Prepare message details
                subject = "Fire Alert"
                message = (
                    f"Hello {contact.first_name} {contact.last_name},\n\n"
                    f"Your dependent, {user.get_full_name}, has triggered an emergency fire alert. "
                    f"They are at {locality}, {town}, {city}, {region}, {country}.\n\n"
                    f"Get it live here:\n"
                    f"https://www.openstreetmap.org/?mlat={location.split(',')[0]}&mlon={location.split(',')[1]}&zoom=15\n\n"
                    "Please respond as soon as possible.\n\nThank you."
                )

                # Send SMS (pseudo code for integration with SMS service)
                try:
                    send_sms(contact.phone_number, message)
                except Exception as e:
                    print(f"Failed to send SMS to {contact.phone_number}: {str(e)}")

                # Send Email
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [contact.email_address],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Failed to send email to {contact.email_address}: {str(e)}")

        # Save emergency action to the database
        try:
            Emergency.objects.create(
                created_by=user,
                action=action,
                location={"latitude": location.split(',')[0], "longitude": location.split(',')[1]},
                country=country,
                region=region,
                city=city,
                town=town,
                locality=locality,
                mission_status="success",
            )
            return Response({"message": "Emergency action successfully logged."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": f"Failed to log emergency action: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
   
        
        