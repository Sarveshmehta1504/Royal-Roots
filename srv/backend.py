import os, re, json, ssl, random, time, uuid, datetime
from dotenv import load_dotenv
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_compress import Compress
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage

load_dotenv()

# ── Firebase ────────────────────────────────────────────────────────────────
def initialize_firebase():
    firebase_service_account = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
    
    if firebase_service_account:
        print(f"🔧 [DEBUG] Found FIREBASE_SERVICE_ACCOUNT (len: {len(firebase_service_account)})")
        try:
            # Handle both JSON string and base64 encoded JSON
            import base64
            # Strip whitespace and quotes that might have been added by mistake
            raw_cred = firebase_service_account.strip()
            if raw_cred.startswith('"') and raw_cred.endswith('"'):
                raw_cred = raw_cred[1:-1]
                
            if not raw_cred.startswith('{'):
                print("🔧 [DEBUG] Attempting base64 decode...")
                raw_cred = base64.b64decode(raw_cred).decode('utf-8')
            
            cred_dict = json.loads(raw_cred)
            print(f"🔧 [DEBUG] Successfully parsed service account for project: {cred_dict.get('project_id')}")
            cred = credentials.Certificate(cred_dict)
        except Exception as e:
            print(f"❌ [ERROR] Failed to parse FIREBASE_SERVICE_ACCOUNT: {str(e)}")
            # Don't raise here, let the fallback or None handle it
            return None
    else:
        print("📂 [DEBUG] No FIREBASE_SERVICE_ACCOUNT env var found, checking local file...")
        CRED_PATH = os.path.join(os.path.dirname(__file__), 'firebase_credentials.json')
        if os.path.exists(CRED_PATH):
            print(f"📂 [DEBUG] Using local file: {CRED_PATH}")
            cred = credentials.Certificate(CRED_PATH)
        else:
            print("❌ [ERROR] No credentials found!")
            return None

    try:
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'swara-2b54e.firebasestorage.app'
            })
            print("🔥 [SUCCESS] Firebase app initialized")
        return True
    except Exception as e:
        print(f"🔥 [ERROR] firebase_admin.initialize_app failed: {e}")
        return None

firebase_initialized = initialize_firebase()
db = firestore.client() if firebase_initialized else None

# ── Gemini ───────────────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# In Netlify functions, this file is inside srv/
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
# current dir is: /var/task/srv, root is 1 level up if srv is at root. 
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))

app = Flask(__name__,
            template_folder=os.path.join(ROOT_DIR, 'scripts/templates'),
            static_folder=ROOT_DIR,
            static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is not set!")

# Production optimisations
Compress(app)
app.config['COMPRESS_MIMETYPES'] = [
    'text/html','text/css','application/javascript','application/json','image/svg+xml'
]
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000 # 1 year for assets by default

# ── Helpers ──────────────────────────────────────────────────────────────────
def requires_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:80]


def _generate_blog(topic: str) -> dict:
    models = [
        'gemini-2.0-flash',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro'
    ]
    prompt = f"""You are an expert SEO copywriter for "Royal Roots Ply", a premium luxury plywood brand in India.
Write a comprehensive, SEO-optimized blog article about: "{topic}"
Return ONLY a valid JSON object with keys:
"title", "meta_desc", "slug", "category", "tag", "excerpt", "read_time", "content" (HTML body paragraphs, no extra wrappers).
Do NOT wrap in markdown code blocks."""
    last_err = None
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            r = model.generate_content(prompt)
            raw = r.text.strip()
            if raw.startswith("```"): raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
            if raw.startswith("json"): raw = raw[4:].strip()
            return json.loads(raw)
        except Exception as e:
            last_err = e
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                raise Exception("Google AI Studio Rate Limit Exceeded: Please wait 60 seconds and try again. (Free Tier Limit Hit)")
    raise Exception(f"All Gemini models failed. Last error: {last_err}")

# ── Auth Routes ───────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET'])
def login():
    if session.get('user_id'):
        return redirect(url_for('admin'))
    return render_template('login.html', firebase_api_key=os.environ.get('FIREBASE_API_KEY', 'YOUR_FIREBASE_API_KEY'))

@app.route('/verify_token', methods=['POST'])
def verify_token():
    token = request.json.get('token')
    try:
        decoded = auth.verify_id_token(token)
        session['user_id'] = decoded['uid']
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── SEO & Meta ──────────────────────────────────────────────────────────────
@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml')

# ── Dynamic Blog Reader ────────────────────────────────────────────────────────
@app.route('/blog/<slug>', strict_slashes=False)
def blog_reader(slug):
    # RESERVED: If the slug is 'index.html' or empty, serve the static Hub
    if slug.lower() in ['index.html', '', 'index']:
        resp = app.send_static_file('blog/index.html')
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return resp
        
    resp = app.make_response(render_template('blog_reader.html', slug=slug))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return resp

# ── Static Pages & Routing ────────────────────────────────────────────────────
@app.route('/')
def index_file():
    resp = app.send_static_file('index.html')
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return resp

@app.route('/<path:path>')
def catch_all(path):
    # If the path exists as a static file, serve it
    # We want HTML files to have no-cache, but other assets to have max-age
    if os.path.isfile(os.path.join(app.static_folder, path)):
        resp = app.send_static_file(path)
        if path.endswith('.html'):
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return resp
    
    # If not found, check if it's a directory (like /blog/)
    if os.path.isdir(os.path.join(app.static_folder, path)):
        index_path = os.path.join(path, 'index.html')
        if os.path.isfile(os.path.join(app.static_folder, index_path)):
            resp = app.send_static_file(index_path)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            return resp

    return "Page Not Found", 404

@app.route('/admin', methods=['GET'])
@requires_auth
def admin():
    return render_template('admin.html')

# ── Blog API ──────────────────────────────────────────────────────────────────
@app.route('/api/blogs', methods=['GET'])
def api_list_blogs():
    """List all blogs from Firestore, most recent first."""
    try:
        docs = db.collection('blogs').order_by(
            'created_at', direction=firestore.Query.DESCENDING
        ).stream()
        blogs = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            # Convert Firestore timestamp to ISO string
            if hasattr(d.get('created_at'), 'isoformat'):
                d['created_at'] = d['created_at'].isoformat()
            blogs.append(d)
        return jsonify(blogs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/blogs/<blog_id>', methods=['GET'])
def api_get_blog(blog_id):
    """Get a single blog by Firestore document ID or by slug."""
    try:
        # Try by doc ID first
        doc = db.collection('blogs').document(blog_id).get()
        if doc.exists:
            d = doc.to_dict(); d['id'] = doc.id
            if hasattr(d.get('created_at'), 'isoformat'):
                d['created_at'] = d['created_at'].isoformat()
            return jsonify(d)
        # Fallback: search by slug
        docs = db.collection('blogs').where('slug', '==', blog_id).limit(1).stream()
        for doc in docs:
            d = doc.to_dict(); d['id'] = doc.id
            if hasattr(d.get('created_at'), 'isoformat'):
                d['created_at'] = d['created_at'].isoformat()
            return jsonify(d)
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/blogs', methods=['POST'])
@requires_auth
def api_create_blog():
    """Create a new blog post in Firestore."""
    data = request.json or {}
    required = ['title', 'content', 'category']
    if not all(data.get(k) for k in required):
        return jsonify({"error": "title, content and category are required"}), 400
    slug = data.get('slug') or _slugify(data['title'])
    doc = {
        'title': data['title'],
        'slug': slug,
        'meta_desc': data.get('meta_desc', ''),
        'category': data['category'],
        'tag': data.get('tag', ''),
        'excerpt': data.get('excerpt', ''),
        'read_time': data.get('read_time', '5 min'),
        'content': data['content'],
        'image_url': data.get('image_url', ''),
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP,
        'published': data.get('published', True),
    }
    ref = db.collection('blogs').document()
    ref.set(doc)
    doc['id'] = ref.id
    return jsonify(doc), 201


@app.route('/api/blogs/<blog_id>', methods=['PUT'])
@requires_auth
def api_update_blog(blog_id):
    """Update an existing blog post."""
    data = request.json or {}
    data['updated_at'] = firestore.SERVER_TIMESTAMP
    db.collection('blogs').document(blog_id).update(data)
    return jsonify({"status": "updated"})


@app.route('/api/blogs/<blog_id>', methods=['DELETE'])
@requires_auth
def api_delete_blog(blog_id):
    """Delete a blog post from Firestore."""
    db.collection('blogs').document(blog_id).delete()
    return jsonify({"status": "deleted"})


@app.route('/api/generate', methods=['POST'])
@requires_auth
def api_generate_blog():
    """AI-generate a blog post and save it to Firestore."""
    topic = (request.json or {}).get('topic', '')
    if not topic:
        return jsonify({"error": "topic is required"}), 400
    try:
        blog_data = _generate_blog(topic)
        blog_data['image_url'] = f"https://source.unsplash.com/1200x630/?{blog_data.get('category','interior').replace(' ','+')}"
        blog_data['published'] = True
        blog_data['created_at'] = firestore.SERVER_TIMESTAMP
        blog_data['updated_at'] = firestore.SERVER_TIMESTAMP
        ref = db.collection('blogs').document()
        ref.set(blog_data)
        blog_data['id'] = ref.id
        return jsonify(blog_data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/upload', methods=['POST'])
@requires_auth
def api_upload_image():
    """Upload a blog image to Firebase Storage and return a public URL."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    ext = os.path.splitext(file.filename)[1].lower()
    allowed = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    if ext not in allowed:
        return jsonify({"error": "File type not allowed"}), 400
    filename = f"blog/{uuid.uuid4().hex}{ext}"
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_file(file, content_type=file.content_type)
    blob.make_public()
    return jsonify({"url": blob.public_url, "path": filename})


# ── Run ────────────────────────────────────────────────────────────────────────
def handler(event, context):
    import serverless_wsgi
    return serverless_wsgi.handle_request(app, event, context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
