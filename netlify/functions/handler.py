import serverless_wsgi
try:
    from server import app
except ImportError:
    # If it's copied during build
    import os
    import sys
    sys.path.append(os.path.dirname(__file__))
    from server import app

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)
