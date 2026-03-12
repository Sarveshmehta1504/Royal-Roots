import firebase_admin
from firebase_admin import credentials, firestore

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()
blogs = list(db.collection('blogs').stream())

images = [
    "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=1400&q=80",
    "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1400&q=80",
    "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1400&q=80",
    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1400&q=80",
    "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=1400&q=80",
    "https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=1400&q=80",
    "https://images.unsplash.com/photo-1622372738946-62e02505feb3?w=1400&q=80",
    "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=1400&q=80",
    "https://images.unsplash.com/photo-1556912172-45b7abe8b7e1?w=1400&q=80",
    "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=1400&q=80",
    "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=1400&q=80",
    "https://images.unsplash.com/photo-1622372738946-62e02505feb3?w=1400&q=80"
]

print(f"Total blogs found: {len(blogs)}")
for i, b in enumerate(blogs):
    img = images[i % len(images)]
    db.collection('blogs').document(b.id).update({'image_url': img})
    print(f"Updated {b.to_dict().get('slug')} with image.")

print("Images updated successfully.")
