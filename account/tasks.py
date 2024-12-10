import requests
import json
from celery import shared_task
from django.conf import settings
import threading
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

@shared_task
def send_sms_task(post_data):
    try:
        HEADERS = {
            'Content-Type': 'application/json',
            'API-KEY': settings.WIGAL_KEY,
            'USERNAME': 'osahene'
        }
        response = requests.post(
            'https://frogapi.wigal.com.gh/api/v3/sms/send',
            headers=HEADERS,
            data=json.dumps(post_data)
        )
        print('emer', response.json())
        return response.json()
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")
        return {"error": str(e)}

@shared_task
def send_email_task(email_messages):
    from django.core.mail import EmailMessage
    try:
        email = EmailMessage(
            subject=email_messages[0],
            body=email_messages[1],
            to=email_messages[3],
            )
        
        email.content_subtype = 'html'        
        EmailThread(email).start()
    except Exception as e:
        print(f"Failed to send email: {str(e)}")