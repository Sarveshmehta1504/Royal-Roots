from firebase_functions import https_fn
from firebase_admin import initialize_app
try:
    from .app import app as flask_app
except ImportError:
    from app import app as flask_app

# The Firebase Functions Python SDK can handle WSGI apps directly in recent versions
# or we can wrap it manually.

@https_fn.on_request()
def backend(req: https_fn.Request) -> https_fn.Response:
    # Werkzeug's Request object (req) is compatible with Flask's dispatch
    with flask_app.request_context(req.environ):
        return flask_app.full_dispatch_request()
