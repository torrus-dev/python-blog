# generate_blog.py

import os
import shutil
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

# Define paths
POSTS_DIR = 'posts'
TEMPLATES_DIR = 'templates'
OUTPUT_DIR = 'output'
ASSETS_DIR = 'assets'
CATEGORY_DIR = os.path.join(OUTPUT_DIR, 'categories')

# Get base URL from environment variable or use default
BASE_URL = os.getenv('BASE_URL', '/')

# Initialize Jinja2 environment
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

# Load templates
try:
    post_template = env.get_template('post_template.html')
    index_template = env.get_template('index_template.html')
    category_template = env.get_template('category_template.html')
except Exception as e:
    print(f"Error loading templates: {e}")
    exit(1)

# Create output directory if it does not exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Copy assets to output directory
shutil.copytree(ASSETS_DIR, os.path.join(OUTPUT_DIR, ASSETS_DIR), dirs_exist_ok=True)

# List markdown files in the posts directory
post_files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')]

# Function to read and parse a markdown file
def parse_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        front_matter, md_content = content.split('---', 2)[1:]
        metadata = yaml.safe_load(front_matter)
        html_content = markdown.markdown(md_content)
    return metadata, html_content

# Generate HTML for each post and categorize them
posts = []
categories = {}
for post_file in post_files:
    filepath = os.path.join(POSTS_DIR, post_file)
    metadata, html_content = parse_markdown_file(filepath)
    post_filename = os.path.splitext(post_file)[0] + '.html'
    output_path = os.path.join(OUTPUT_DIR, post_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(post_template.render(metadata=metadata, content=html_content, base_url=BASE_URL, categories=categories.keys()))
    posts.append({'filename': post_filename, 'title': metadata['title'], 'date': metadata['date'], 'category': metadata['category']})
    # Categorize posts
    category = metadata['category']
    if category not in categories:
        categories[category] = []
    categories[category].append({'filename': post_filename, 'title': metadata['title'], 'date': metadata['date']})

# Generate the index page
index_html = index_template.render(posts=sorted(posts, key=lambda x: x['date'], reverse=True), categories=categories.keys(), base_url=BASE_URL)
with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)

# Generate category pages
for category, category_posts in categories.items():
    category_output_path = os.path.join(CATEGORY_DIR, f"{category}.html")
    os.makedirs(os.path.dirname(category_output_path), exist_ok=True)
    category_html = category_template.render(category=category, posts=sorted(category_posts, key=lambda x: x['date'], reverse=True), base_url=BASE_URL, categories=categories.keys())
    with open(category_output_path, 'w', encoding='utf-8') as f:
        f.write(category_html)

print("Blog generated successfully.")
