import serverless_wsgi
import os
import sys
sys.path.append(os.path.dirname(__file__))
from app_logic import app

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)
