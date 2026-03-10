import os
import re
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
    exit(1)

genai.configure(api_key=api_key)

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "scripts", "blog_template.html")
BLOG_DIR = os.path.join(BASE_DIR, "blog")
BLOG_INDEX_PATH = os.path.join(BLOG_DIR, "index.html")
HOME_INDEX_PATH = os.path.join(BASE_DIR, "index.html")

def generate_blog_content(topic):
    print(f"Generating blog post for: '{topic}'...")
    
    # Initialize the model
    # We use gemini-1.5-pro as it is great for writing rich content and following JSON schema
    # We use gemini-2.5-flash-lite for speed and generous rate limits
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    prompt = f"""
    You are an expert SEO copywriter and interior design/plywood specialist for "Royal Roots Ply", a premium plywood brand in India.
    
    Please write a comprehensive, SEO-optimized blog article about: "{topic}"
    
    The output MUST be a valid JSON object with the following keys exactly:
    - "title": The SEO title (under 60 chars)
    - "meta_desc": A compelling meta description (under 155 chars)
    - "slug": A URL-friendly slug (lowercase, hyphenated, no special chars, e.g., "benefits-of-marine-plywood")
    - "category": A 1-2 word category (e.g., "Plywood Guide", "Interior Tips", "Buying Guide")
    - "tag": A very short 1-word tag for the card label (e.g., "Plywood", "Kitchen", "Care")
    - "excerpt": A 2-sentence summary for the blog card.
    - "read_time": Estimated reading time in minutes (number only as string, e.g., "5").
    - "content": The actual article body written in HTML. 
      - Please use <h2> and <h3> for headers.
      - Use <p> for paragraphs.
      - Use <ul>, <ol>, and <li> for lists.
      - Use <blockquote> for important pull quotes.
      - Do NOT include wrapping <html>, <head>, <body>, or <main> tags, JUST the content that will go inside the <div class="article-content"> snippet.
      - Make the content rich, engaging, and professional. Mention "Royal Roots Ply" naturally where appropriate as a premium IS:710 provider.

    Return ONLY the raw JSON object. Do not wrap it in markdown codeblocks like ```json ... ```. 
    Just output the raw JSON string starting with {{ and ending with }}.
    """
    
    try:
        response = model.generate_content(prompt)
    except Exception as e:
        if "ResourceExhausted" in str(type(e)) or "429" in str(e):
            print("\n" + "="*50)
            print("ERROR: API Quota Exceeded or API billing is not enabled.")
            print("The API key provided does not have enough quota to run the AI model.")
            print("Please check your Google AI Studio dashboard to enable billing or use a different key.")
            print("="*50 + "\n")
        else:
            print(f"Error calling Gemini API: {e}")
        exit(1)
    
    try:
        raw_text = response.text.strip()
        # Clean up any markdown formatting if present
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json\n", "")
            raw_text = raw_text.replace("```", "")
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```\n", "")
            raw_text = raw_text.replace("```", "")
            
        data = json.loads(raw_text)
        return data
    except Exception as e:
        print("Error parsing AI output. The AI might not have returned valid JSON.")
        print("Raw output:", response.text)
        print("Exception:", str(e))
        exit(1)

def create_html_file(blog_data):
    print(f"Creating HTML file for slug: {blog_data['slug']}...")
    
    with open(TEMPLATE_PATH, "r") as f:
        template = f.read()
        
    now = datetime.now()
    date_iso = now.strftime("%Y-%m-%d")
    date_formatted = now.strftime("%B %d, %Y")
    
    html_content = template.replace("{{TITLE}}", blog_data["title"])
    html_content = html_content.replace("{{META_DESC}}", blog_data["meta_desc"])
    html_content = html_content.replace("{{SLUG}}", blog_data["slug"])
    html_content = html_content.replace("{{CATEGORY}}", blog_data["category"])
    html_content = html_content.replace("{{DATE}}", date_iso)
    html_content = html_content.replace("{{DATE_FORMATTED}}", date_formatted)
    html_content = html_content.replace("{{READ_TIME}}", blog_data["read_time"])
    html_content = html_content.replace("{{CONTENT}}", blog_data["content"])
    
    file_path = os.path.join(BLOG_DIR, f"{blog_data['slug']}.html")
    with open(file_path, "w") as f:
        f.write(html_content)
        
    print(f"Successfully generated: {file_path}")
    return file_path

def generate_card_html(blog_data, is_homepage=False):
    link_prefix = "blog/" if is_homepage else ""
    return f"""
                <article class="blog-card reveal">
                    <div class="blog-card__image"><span class="blog-card__image-label">{blog_data['category']}</span></div>
                    <div class="blog-card__body">
                        <span class="blog-card__tag">{blog_data['tag']}</span>
                        <h3 class="blog-card__title">{blog_data['title']}</h3>
                        <p class="blog-card__excerpt">{blog_data['excerpt']}</p>
                        <a href="{link_prefix}{blog_data['slug']}.html" class="cta-link">Read More &rarr;</a>
                    </div>
                </article>
"""

def update_blog_index(blog_data):
    print("Updating blog/index.html...")
    with open(BLOG_INDEX_PATH, "r") as f:
        soup = BeautifulSoup(f, "html.parser")
        
    grid = soup.find(class_="blog-listing__grid")
    if grid:
        # Prepend the new card
        new_card_html = generate_card_html(blog_data, is_homepage=False)
        new_card_soup = BeautifulSoup(new_card_html, "html.parser")
        grid.insert(0, new_card_soup)
        
        with open(BLOG_INDEX_PATH, "w") as f:
            # Prettify usually breaks existing formatting heavily, so we'll write the raw soup string
            f.write(str(soup))
        print("Successfully updated blog/index.html")
    else:
        print("Could not find .blog-listing__grid in blog/index.html")

def update_home_index(blog_data):
    print("Updating index.html...")
    with open(HOME_INDEX_PATH, "r") as f:
        soup = BeautifulSoup(f, "html.parser")
        
    # Find the section by ID or unique class. The Expert Guides section has a specific structure.
    # Searching for the container of the blog cards in home index
    guides_section_heading = soup.find(lambda tag: tag.name == "h2" and "Expert Guides" in tag.text)
    if not guides_section_heading:
        print("Could not find 'Expert Guides' section heading in index.html")
        return
        
    # Traverse to find the grid which is a sibling or child of the parent container
    parent_section = guides_section_heading.find_parent("section")
    if not parent_section:
         print("Could not find the parent section for Expert Guides")
         return
         
    grid = parent_section.find(class_="blog-preview__grid")
    if grid:
        new_card_html = generate_card_html(blog_data, is_homepage=True)
        new_card_soup = BeautifulSoup(new_card_html, "html.parser")
        
        # Insert at the beginning
        grid.insert(0, new_card_soup)
        
        # Remove the 4th child to keep it at 3 articles maximum on the homepage
        articles = grid.find_all("article", class_="blog-card")
        if len(articles) > 3:
            articles[-1].extract()
            
        with open(HOME_INDEX_PATH, "w") as f:
            f.write(str(soup))
        print("Successfully updated index.html")
    else:
         print("Could not find .blog-preview__grid in index.html")


if __name__ == "__main__":
    print("-" * 50)
    print("Royal Roots AI Blog Studio")
    print("-" * 50)
    
    topic = input("Enter the blog topic (e.g. 'How to clean an acrylic kitchen'): ")
    if not topic.strip():
        print("Topic cannot be empty.")
        exit(1)
        
    blog_data = generate_blog_content(topic)
    create_html_file(blog_data)
    update_blog_index(blog_data)
    update_home_index(blog_data)
    
    print("-" * 50)
    print("SUCCESS! Blog published locally.")
    print("Review the files, then deploy to your web host.")
    print("-" * 50)
