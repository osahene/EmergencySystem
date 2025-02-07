from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import GoogleSignInSerializer
from rest_framework.response import Response
from rest_framework import status


class GoogleOauthSignInview(GenericAPIView):
    serializer_class=GoogleSignInSerializer

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=serializer.validated_data
        if not data.get('is_phone_verified', False):
            return Response(
                {'message': 'Phone number not verified', 'redirect_url': '/auth/phone-number', 'data': data['tokens']}, 
                status=status.HTTP_307_TEMPORARY_REDIRECT
            )
        
        return Response(data, status=status.HTTP_200_OK)
        



# class FacebookSocialAuthView(GenericAPIView):

#     serializer_class = FacebookSocialAuthSerializer

#     def post(self, request):
#         """

#         POST with "auth_token"

#         Send an access token as from facebook to get user information

#         """

#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = ((serializer.validated_data)['auth_token'])
#         return Response(data, status=status.HTTP_200_OK)


# class TwitterSocialAuthView(GenericAPIView):
#     serializer_class = TwitterAuthSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.validated_data, status=status.HTTP_200_OK)
