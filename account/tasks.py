import requests
import json
from celery import shared_task
from django.conf import settings

@shared_task
def send_sms_task(post_data, headers=settings.HEADERS):
    try:
        response = requests.post(
            'https://frogapi.wigal.com.gh/api/v3/sms/send',
            headers=headers,
            data=json.dumps(post_data)
        )
        return response.json()
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")
        return {"error": str(e)}

@shared_task
def send_email_task(email_messages):
    from django.core.mail import send_mail
    try:
        send_mail(email_messages, fail_silently=False)
    except Exception as e:
        print(f"Failed to send email: {str(e)}")