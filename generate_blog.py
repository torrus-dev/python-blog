import os
import shutil
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

# Define paths
POSTS_DIR = "posts"
TEMPLATES_DIR = "templates"
OUTPUT_DIR = "output"
ASSETS_DIR = "assets"
CATEGORY_DIR = os.path.join(OUTPUT_DIR, "categories")

# Get base URL from environment variable or use default
BASE_URL = os.getenv("BASE_URL", "/")


def load_templates(env):
    """Load templates using Jinja2 environment."""
    try:
        post_template = env.get_template("post_template.html")
        index_template = env.get_template("index_template.html")
        category_template = env.get_template("category_template.html")
    except Exception as e:
        print(f"Error loading templates: {e}")
        exit(1)
    return post_template, index_template, category_template


def create_output_directory(output_dir):
    """Create output directory if it does not exist."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def copy_assets(assets_dir, output_dir):
    """Copy assets to output directory."""
    shutil.copytree(assets_dir, os.path.join(output_dir, assets_dir), dirs_exist_ok=True)


def list_markdown_files(posts_dir):
    """List markdown files in the posts directory."""
    return [f for f in os.listdir(posts_dir) if f.endswith(".md")]


def parse_markdown_file(filepath):
    """Read and parse a markdown file."""
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
        front_matter, md_content = content.split("---", 2)[1:]
        metadata = yaml.safe_load(front_matter)
        html_content = markdown.markdown(md_content)
    return metadata, html_content


def generate_post_html(post_template, metadata, html_content, post_filename, output_dir, categories):
    """Generate HTML for a single post."""
    output_path = os.path.join(output_dir, post_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(
            post_template.render(
                metadata=metadata,
                content=html_content,
                base_url=BASE_URL,
                categories=categories,
            )
        )


def generate_index_page(index_template, posts, categories, output_dir):
    """Generate the index page."""
    index_html = index_template.render(
        posts=sorted(posts, key=lambda x: x["date"], reverse=True),
        categories=categories,
        base_url=BASE_URL,
    )
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)


def generate_category_pages(category_template, categories, output_dir):
    """Generate pages for each category."""
    for category, category_posts in categories.items():
        category_output_path = os.path.join(CATEGORY_DIR, f"{category}.html")
        os.makedirs(os.path.dirname(category_output_path), exist_ok=True)
        category_html = category_template.render(
            category=category,
            posts=sorted(category_posts, key=lambda x: x["date"], reverse=True),
            base_url=BASE_URL,
            categories=categories.keys(),
        )
        with open(category_output_path, "w", encoding="utf-8") as f:
            f.write(category_html)


def main():
    # Initialize Jinja2 environment
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    # Load templates
    post_template, index_template, category_template = load_templates(env)

    # Create output directory
    create_output_directory(OUTPUT_DIR)

    # Copy assets
    copy_assets(ASSETS_DIR, OUTPUT_DIR)

    # List markdown files
    post_files = list_markdown_files(POSTS_DIR)

    # Generate HTML for each post and categorize them
    posts = []
    categories = {}
    for post_file in post_files:
        filepath = os.path.join(POSTS_DIR, post_file)
        metadata, html_content = parse_markdown_file(filepath)
        post_filename = os.path.splitext(post_file)[0] + ".html"
        category = metadata["category"].capitalize()
        # Categorize posts
        if category not in categories:
            categories[category] = []
        categories[category].append(
            {
                "filename": post_filename,
                "title": metadata["title"],
                "date": metadata["date"],
            }
        )
        posts.append(
            {
                "filename": post_filename,
                "title": metadata["title"],
                "date": metadata["date"],
                "category": category,
            }
        )
        generate_post_html(post_template, metadata, html_content, post_filename, OUTPUT_DIR, categories.keys())

    # Generate the index page
    generate_index_page(index_template, posts, categories.keys(), OUTPUT_DIR)

    # Generate category pages
    generate_category_pages(category_template, categories, OUTPUT_DIR)

    print("Blog generated successfully.")


if __name__ == "__main__":
    main()
