#!/bin/bash
gunicorn EmergencyBackend.wsgi
celery -A EmergencyBackend worker -l info