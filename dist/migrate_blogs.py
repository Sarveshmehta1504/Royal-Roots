import os, re
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

cred = credentials.Certificate('firebase_credentials.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

BLOG_DIR = 'blog'
files = [f for f in os.listdir(BLOG_DIR) if f.endswith('.html') and f != 'index.html']

for f in files:
    path = os.path.join(BLOG_DIR, f)
    with open(path, 'r', encoding='utf-8') as html_file:
        soup = BeautifulSoup(html_file, 'html.parser')
    
    # Title
    title_tag = soup.find('h1', class_='hero-title')
    title = title_tag.text.strip() if title_tag else soup.title.string.replace(' | Royal Roots AI', '').strip()
    
    # Meta Description & Excerpt
    meta_desc = ''
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag:
        meta_desc = meta_tag['content'].strip()
    excerpt = meta_desc
    
    # Slug
    slug = f.replace('.html', '')
    
    # Category / Tag
    category = 'Plywood Guide'
    cat_badge = soup.find('span', class_='category-badge')
    if cat_badge:
        category = cat_badge.text.strip()
        
    tag = category
    
    # Read Time
    read_time = '5 min'
    meta_div = soup.find('div', class_='hero-meta')
    if meta_div:
        for span in meta_div.find_all('span'):
            if 'min read' in span.text:
                read_time = span.text.strip()
                
    # Content
    content = ''
    main_tag = soup.find('main', class_='article-body')
    if main_tag:
        content = ''.join([str(child) for child in main_tag.children])
    else:
        print(f"Skipping {f} - No <main class='article-body'> found.")
        continue
        
    # Image URL
    image_url = 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1400&q=80'
    hero = soup.find('header', class_='article-hero')
    if hero and hero.has_attr('style'):
        style = hero['style']
        match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
        if match:
            url_path = match.group(1).replace('../', '/')
            image_url = url_path
            
    # Save to Firestore
    doc = {
        'title': title,
        'slug': slug,
        'meta_desc': meta_desc,
        'category': category,
        'tag': tag,
        'excerpt': excerpt,
        'read_time': read_time,
        'content': content.strip(),
        'image_url': image_url,
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP,
        'published': True
    }
    
    # Check if exists
    existing = list(db.collection('blogs').where('slug', '==', slug).limit(1).stream())
    if existing:
        ref = db.collection('blogs').document(existing[0].id)
        ref.update(doc)
        print(f"Updated {slug}")
    else:
        ref = db.collection('blogs').document()
        ref.set(doc)
        print(f"Created {slug}")

print("Migration complete!")
