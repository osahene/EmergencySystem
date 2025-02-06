from rest_framework import serializers
from .helpers import Google, register_social_user
from EmergencyBackend.settings import GOOGLE_CLIENT_ID
from rest_framework.exceptions import AuthenticationFailed

class GoogleSignInSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    # user_type = serializers.ChoiceField(choices=['user', 'company'])

    def validate(self, attrs):
        access_token = attrs.get('access_token')
        # user_type = attrs.get('user_type' = "user")
        user_data = Google.validate(access_token)
        first_name, last_name,  email, phone_number,= Google.get_user_info(access_token)

        try:
            user_data['sub']
        except KeyError:
            raise serializers.ValidationError("The token has expired or is invalid. Please try again.")
        
        if user_data['aud'] != GOOGLE_CLIENT_ID:
            raise AuthenticationFailed('Could not verify user.')

        return register_social_user('google', email, first_name, last_name, phone_number)
