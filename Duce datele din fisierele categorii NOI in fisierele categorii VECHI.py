
##  SA ADAUGI TOATE FISIERELE DE TIP CATEGORII inainte de toate

import os
import re
from bs4 import BeautifulSoup
import html

# Define the source and destination directories
source_dir = r'e:\Carte\BB\17 - Site Leadership\Principal 2022\en'
dest_dir = r'e:\Carte\BB\17 - Site Leadership\Principal\en\exceptions'

# List of files to process
files_to_process = [
    'leadership-quantum-xx.html',
    'leadership-y4-titanium.html',
    'leadership-r2-premiere.html',
    'leadership-mindware.html',
    'leadership-z3-extended.html',
    'leadership-xs-analytics.html',
    'leadership-s4-quartz.html',
    'leadership-x3-silver.html',
    'leadership-impact.html',
    'top-leadership.html',
    'leadership-plus.html',
    'leadership-that-lasts.html',
    'total-leadership.html',
    'hr-human-resources.html',
    'successful-leadership.html',
    'leadership-magic.html',
    'leadership-and-attitude.html',
    'leadership-know-how.html'
]

def fix_special_characters(text):
    """
    Fix common encoding issues with special characters using Unicode code points
    instead of direct string literals to avoid syntax errors.
    """
    # Common UTF-8 double-encoded characters using Unicode code points
    replacements = [
        # Lowercase accented characters
        (b'\xc3\x83\xc2\xa9', 'é'),  # e-acute
        (b'\xc3\x83\xc2\xa8', 'è'),  # e-grave
        (b'\xc3\x83\xc2\xa2', 'â'),  # a-circumflex
        (b'\xc3\x83\xc2\xaa', 'ê'),  # e-circumflex
        (b'\xc3\x83\xc2\xae', 'î'),  # i-circumflex
        (b'\xc3\x83\xc2\xb4', 'ô'),  # o-circumflex
        (b'\xc3\x83\xc2\xbb', 'û'),  # u-circumflex
        (b'\xc3\x83\xc2\xb9', 'ù'),  # u-grave
        (b'\xc3\x83\xc2\xa7', 'ç'),  # c-cedilla

        # Uppercase accented characters
        (b'\xc3\x83\xc2\x80', 'À'),  # A-grave
        (b'\xc3\x83\xc2\x82', 'Â'),  # A-circumflex
        (b'\xc3\x83\xc2\x84', 'Ä'),  # A-diaeresis
        (b'\xc3\x83\xc2\x85', 'Å'),  # A-ring
        (b'\xc3\x83\xc2\x89', 'É'),  # E-acute

        # Special case - the one causing the error
        (b'\xc3\x83\xe2\x80\x99', 'Ñ'),  # N-tilde
    ]

    # A simpler approach: direct replacements for known problematic cases
    direct_replacements = {
        'Ã©': 'é',  # e-acute - for Areté
        'Ã¨': 'è',  # e-grave
        'Ã¢': 'â',  # a-circumflex
        'Ãª': 'ê',  # e-circumflex
        'Ã®': 'î',  # i-circumflex
        'Ã´': 'ô',  # o-circumflex
        'Ã»': 'û',  # u-circumflex
        'Ã¹': 'ù',  # u-grave
        'Ã§': 'ç',  # c-cedilla
    }

    # Apply direct replacements
    for wrong, correct in direct_replacements.items():
        if wrong in text:
            text = text.replace(wrong, correct)

    # Special handling for the problematic 'Ñ' character
    if 'AretÃ©' in text:
        text = text.replace('AretÃ©', 'Areté')

    return text

def extract_articles_from_source(file_path):
    """Extract article information from the source file format (2022)"""
    try:
        # Try different encodings if needed
        content = None
        encodings = ['utf-8', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                    break
            except UnicodeDecodeError:
                continue

        if content is None:
            print(f"Error: Could not read {file_path} with any encoding")
            return []

        # Create a soup object for the entire content
        soup = BeautifulSoup(content, 'html.parser')

        # Find all article elements directly
        article_elements = soup.find_all('article', class_='blog-box')

        if not article_elements:
            print(f"Warning: No articles found in {file_path}")
            return []

        articles = []

        for article in article_elements:
            try:
                # Extract article information
                title_link = article.select_one('h2.custom-h1 a')
                title = title_link.text.strip() if title_link else "Unknown Title"
                # Fix special characters in title
                title = fix_special_characters(title)

                url = title_link['href'] if title_link and 'href' in title_link.attrs else "#"

                # Extract date
                time_elem = article.select_one('time')
                date_text = time_elem.text.strip() if time_elem else "Unknown Date"

                # Extract category
                category_link = article.select_one('a.color-green')
                category = category_link.text.strip() if category_link else "Unknown Category"
                category_url = category_link['href'] if category_link and 'href' in category_link.attrs else "#"

                # Extract description
                description = article.select_one('p.mb-35px').text.strip() if article.select_one('p.mb-35px') else ""
                # Fix special characters in description
                description = fix_special_characters(description)

                articles.append({
                    'title': title,
                    'url': url,
                    'date': date_text,
                    'category': category,
                    'category_url': category_url,
                    'description': description
                })

                print(f"  - Found article: '{title}'")
            except Exception as e:
                print(f"Error processing article: {e}")

        return articles
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

def format_articles_for_destination(articles, category_file):
    """Format the articles in the destination format"""

    output = []
    output.append("<!-- ARTICOL CATEGORIE START -->")
    output.append('<div align="justify">')

    for article in articles:
        # Article title
        output.append('    <table width="638" border="0">')
        output.append('        <tr>')
        output.append(f'          <td><span class="den_articol"><a href="{article["url"]}" class="linkMare">{article["title"]}</a></span></td>')
        output.append('          </tr>')
        output.append('          <tr>')
        output.append(f'          <td class="text_dreapta">{article["date"]}, in <a href="{article["category_url"]}" title="View all articles from {article["category"]}" class="external" rel="category tag">{article["category"]}</a>, by Neculai Fantanaru</td>')
        output.append('        </tr>')
        output.append('      </table>')

        # Description
        output.append(f'      <p class="text_obisnuit2"><em>{article["description"]}</em></p>')

        # Read more link
        output.append('      <table width="552" border="0">')
        output.append('        <tr>')
        output.append(f'          <td width="552"><div align="right" id="external2"><a href="{article["url"]}">read more </a><a href="https://neculaifantanaru.com/en/" title=""><img src="Arrow3_black_5x7.gif" alt="" width="5" height="7" class="arrow" /></a></div></td>')
        output.append('        </tr>')
        output.append('      </table>')
        output.append('      <p class="text_obisnuit"></p>')

    # Close the container
    output.append('          </div>')
    output.append('          <p align="justify" class="text_obisnuit style3"> </p>')
    output.append('<!-- ARTICOL CATEGORIE FINAL -->')

    return '\n'.join(output)

def process_file(filename):
    """Process a single file, converting from 2022 format to the old format"""
    source_path = os.path.join(source_dir, filename)
    dest_path = os.path.join(dest_dir, filename)

    # Extract articles from source file
    articles = extract_articles_from_source(source_path)
    print(f"Found {len(articles)} articles in {source_path}")

    # If destination file exists, read it to find the insertion points
    if os.path.exists(dest_path):
        # Try different encodings for reading the destination file
        dest_content = None
        successful_encoding = None
        encodings = ['utf-8', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(dest_path, 'r', encoding=encoding) as file:
                    dest_content = file.read()
                    successful_encoding = encoding
                    break
            except UnicodeDecodeError:
                continue

        if dest_content is None:
            print(f"Error: Could not read {dest_path} with any encoding")
            return

        # Find the content between markers
        pattern = r'<!-- ARTICOL CATEGORIE START -->(.+?)<!-- ARTICOL CATEGORIE FINAL -->'
        match = re.search(pattern, dest_content, re.DOTALL)

        if match:
            # Format the articles in the destination format
            new_content = format_articles_for_destination(articles, filename)

            # Replace the old content with the new content
            updated_content = dest_content.replace(match.group(0), new_content)

            # Ensure meta charset is set to UTF-8
            if '<meta charset="' in updated_content and not '<meta charset="UTF-8"' in updated_content:
                updated_content = re.sub(r'<meta charset="[^"]*"', '<meta charset="UTF-8"', updated_content)
            elif not '<meta charset=' in updated_content and '<head>' in updated_content:
                updated_content = updated_content.replace('<head>', '<head>\n<meta charset="UTF-8">')

            # Add proper HTML5 doctype if missing
            if not updated_content.strip().startswith('<!DOCTYPE html>'):
                updated_content = '<!DOCTYPE html>\n' + updated_content

            # Write the updated content back to the destination file using UTF-8
            try:
                with open(dest_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)

                print(f"Updated {dest_path} with {len(articles)} articles (UTF-8 encoding)")
            except Exception as e:
                print(f"Error writing to {dest_path}: {e}")
        else:
            print(f"Warning: Could not find article section markers in {dest_path}")
    else:
        print(f"Error: Destination file {dest_path} does not exist")

def main():
    """Main function to process all files"""
    print("Starting article migration...")

    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Process each file
    for filename in files_to_process:
        print(f"\nProcessing {filename}...")
        process_file(filename)

    print("\nArticle migration completed!")

if __name__ == "__main__":
    main()