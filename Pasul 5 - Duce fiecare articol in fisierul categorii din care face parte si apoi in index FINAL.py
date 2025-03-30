import os
import re
import shutil
from bs4 import BeautifulSoup
from pathlib import Path
import datetime
from datetime import datetime, timedelta

def read_file_with_fallback_encoding(file_path):
    """Read file using various encodings to handle diacritics."""
    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    content = None

    filename = os.path.basename(file_path)
    print(f"  [Debug] Attempting to read file: {filename}")

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                print(f"  [Debug] File '{filename}' read successfully with encoding: {encoding}")
                break
        except UnicodeDecodeError:
            print(f"  [Debug] Error reading '{filename}' with encoding: {encoding}")
            continue

    if content is None:
        print(f"ERROR: Could not read file {filename} with any available encoding.")

    return content

def write_file_with_encoding(file_path, content):
    """Write file with UTF-8 encoding."""
    filename = os.path.basename(file_path)
    try:
        # Fix spacing between p and table tags
        content = fix_spacing_between_tags(content)

        # Fix div tag alignment
        content = fix_div_alignment(content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [Debug] File '{filename}' written successfully with UTF-8 encoding")
        return True
    except Exception as e:
        print(f"  [Error] Failed to write file '{filename}': {str(e)}")
        return False

def fix_spacing_between_tags(content):
    """Fix spacing between p and table tags to ensure correct formatting."""
    # Replace any instances of </p> followed by one or more whitespace and then <table
    # with </p> followed by a single newline and the correct spacing before <table
    fixed_content = re.sub(r'<p class="text_obisnuit"></p>\s+<table width=',
                          r'<p class="text_obisnuit"></p>\n    <table width=',
                          content)
    return fixed_content

def fix_div_alignment(content):
    """Fix div tag alignment to ensure consistent formatting."""
    # Fix </div> tag alignment
    fixed_content = re.sub(r'<p class="text_obisnuit"></p>\s*</div>\s*<p align',
                          r'<p class="text_obisnuit"></p>\n          </div>\n          <p align',
                          content)
    return fixed_content

def fix_special_characters(text):
    """Fix common encoding issues with special characters."""
    # Direct replacements for known problematic cases
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

def extract_article_info(article_content):
    """Extract article title, date, and category information from the article file."""
    # Fix special characters first
    article_content = fix_special_characters(article_content)

    # Use BeautifulSoup for more reliable HTML parsing
    soup = BeautifulSoup(article_content, 'html.parser')

    # Extract article title
    title_tag = soup.find('h1', class_='den_articol')
    if not title_tag:
        print("  [Error] Could not find article title")
        return None

    title = title_tag.get_text().strip()

    # Extract canonical URL
    canonical_link = soup.find('link', rel='canonical')
    if not canonical_link:
        print("  [Error] Could not find canonical URL")
        return None

    canonical_url = canonical_link.get('href')
    if not canonical_url:
        print("  [Error] Canonical URL is empty")
        return None

    # Extract article filename from canonical URL
    article_filename = os.path.basename(canonical_url)

    # Extract date and category
    date_category_tag = soup.find('td', class_='text_dreapta')
    if not date_category_tag:
        print("  [Error] Could not find date and category information")
        return None

    date_category_text = date_category_tag.get_text().strip()

    # Extract date - look for date with year format first
    date_match = re.search(r'On (.*?, \d{4}),', date_category_text)
    if not date_match:
        # Try without year format
        date_match = re.search(r'On (.*?),', date_category_text)
        if not date_match:
            print("  [Error] Could not extract date")
            return None

    date = date_match.group(1).strip()

    # Make sure the date includes the year
    if not re.search(r'\d{4}$', date):
        # If year is missing, append current year
        date = f"{date}, 2025"
        print(f"  [Debug] Added year to date: {date}")

    # Extract category link
    category_link_tag = date_category_tag.find('a')
    if not category_link_tag:
        print("  [Error] Could not find category link")
        return None

    category_link = category_link_tag.get('href')
    category_name = category_link_tag.get_text().strip()

    # Try to find a quote
    quote = find_and_extract_quote(soup)

    # Extract year from date
    year_match = re.search(r'(\d{4})', date)
    article_year = int(year_match.group(1)) if year_match else 2025

    # Parse the date into a datetime object for comparison
    month_match = re.search(r'([A-Za-z]+) (\d+)', date)
    if month_match:
        month_name = month_match.group(1)
        day = int(month_match.group(2))

        # Convert month name to number
        months = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        month = months.get(month_name, 1)
    else:
        month = 1
        day = 1

    # Create a sort key for date ordering
    sort_key = f"{article_year:04d}{month:02d}{day:02d}"

    # Create a datetime object for date comparison
    article_date = datetime(article_year, month, day)

    return {
        'title': title,
        'date': date,
        'category_link': category_link,
        'category_name': category_name,
        'article_url': canonical_url,
        'article_filename': article_filename,
        'quote_text': quote,
        'year': article_year,             # Store the year for sorting
        'sort_key': sort_key,             # Store the sort key for precise date ordering
        'datetime': article_date,         # Store the datetime object for comparison
        'html_content': article_content   # Store the full HTML content
    }

def find_and_extract_quote(soup):
    """Try to find a quote in the article content using BeautifulSoup object."""
    # Look for paragraphs with italic content
    em_tags = soup.find_all('em')
    for em in em_tags:
        text = em.get_text().strip()
        if text and len(text) > 20:  # A reasonable quote length
            return text

    # If no italicized text found, look for first paragraph
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text().strip()
        if text and len(text) > 20:  # A reasonable quote length
            return text

    return None

def extract_category_filename(category_link):
    """Extract the category filename from the category link."""
    if not category_link:
        return None

    return os.path.basename(category_link)

def create_new_article_entry(article_info, width="638"):
    """Create a new article entry HTML block."""
    # Check if we have the quote text
    quote_html = ""
    if article_info.get('quote_text'):
        quote_html = f"<p class=\"text_obisnuit2\"><em>{article_info['quote_text']}</em></p>"
    else:
        quote_html = "<p class=\"text_obisnuit2\"><em>True knowledge begins where you dare to transcend the limits imposed by the teachings of others.</em></p>"

    # Ensure date format is consistent and includes year
    date = article_info['date']
    if not re.search(r'\d{4}$', date):
        date = f"{date}, 2025"

    article_entry = f"    <table width=\"{width}\" border=\"0\">\n        <tr>\n          <td><span class=\"den_articol\"><a href=\"{article_info['article_url']}\" class=\"linkMare\">{article_info['title']}</a></span></td>\n          </tr>\n          <tr>\n          <td class=\"text_dreapta\">On {date}, in <a href=\"{article_info['category_link']}\" title=\"View all articles from {article_info['category_name']}\" class=\"external\" rel=\"category tag\">{article_info['category_name']}</a>, by Neculai Fantanaru</td>\n        </tr>\n      </table>\n      {quote_html}\n      <table width=\"552\" border=\"0\">\n        <tr>\n          <td width=\"552\"><div align=\"right\" id=\"external2\"><a href=\"{article_info['article_url']}\">read more </a><a href=\"https://neculaifantanaru.com/en/\" title=\"\"><img src=\"Arrow3_black_5x7.gif\" alt=\"\" width=\"5\" height=\"7\" class=\"arrow\" /></a></div></td>\n        </tr>\n      </table>\n      <p class=\"text_obisnuit\"></p>"

    return article_entry

def extract_existing_urls(category_content):
    """Extract all existing article URLs from a category file."""
    existing_urls = []

    # Fix special characters to ensure consistent matching
    category_content = fix_special_characters(category_content)

    # Look for all article links
    pattern = r'<span class="den_articol"><a href="(https://neculaifantanaru\.com/en/[^"]+)"'
    matches = re.finditer(pattern, category_content)

    for match in matches:
        url = match.group(1)
        existing_urls.append(url)

    return existing_urls

def analyze_category_file(content):
    """Analyze category file to determine its structure."""
    # Find the start marker
    start_marker = "<!-- ARTICOL CATEGORIE START -->"
    if start_marker not in content:
        return None

    # Find the end marker
    end_marker = "<!-- ARTICOL CATEGORIE FINAL -->"
    has_end_marker = end_marker in content

    # Find opening div
    opening_div_match = re.search(r'<!-- ARTICOL CATEGORIE START -->\s*<div align="justify">', content)
    has_opening_div = bool(opening_div_match)

    # Find closing div and paragraph before end marker
    closing_pattern = r'</div>\s*<p[^>]*>\s*</p>\s*<!-- ARTICOL CATEGORIE FINAL -->'
    closing_match = re.search(closing_pattern, content)
    has_closing_structure = bool(closing_match)

    # Find table width
    table_width_match = re.search(r'<table width="(\d+)" border="0">', content)
    table_width = table_width_match.group(1) if table_width_match else "638"

    return {
        'has_start_marker': True,
        'has_end_marker': has_end_marker,
        'has_opening_div': has_opening_div,
        'has_closing_structure': has_closing_structure,
        'table_width': table_width
    }

def update_category_file(category_file_path, article_entries_by_year):
    """Update the category file with new article entries sorted by date."""
    content = read_file_with_fallback_encoding(category_file_path)
    if not content:
        return False

    # Fix special characters
    content = fix_special_characters(content)

    # Extract existing URLs to avoid duplicates
    existing_urls = extract_existing_urls(content)

    # Get all existing articles with their dates
    existing_articles = extract_existing_articles(content)

    # Filter and prepare new articles
    new_articles = []
    for year, entries in article_entries_by_year.items():
        for entry_info in entries:
            if entry_info['url'] not in existing_urls:
                article_date = entry_info['info']['datetime']
                new_articles.append({
                    'date': article_date,
                    'entry': create_new_article_entry(entry_info['info'])
                })

    if not new_articles:
        print(f"  [Info] No new articles to add after filtering duplicates")
        return True

    # Combine existing and new articles
    all_articles = existing_articles + new_articles

    # Sort all articles by date (newest first)
    all_articles.sort(key=lambda x: x['date'], reverse=True)

    # Analyze file structure
    analysis = analyze_category_file(content)
    if not analysis:
        print(f"  [Error] Could not analyze category file structure")
        return False

    # Find the start marker
    start_marker = "<!-- ARTICOL CATEGORIE START -->"
    parts = content.split(start_marker, 1)
    if len(parts) != 2:
        print(f"  [Error] Invalid content format in category file")
        return False

    before_marker = parts[0]
    after_marker = parts[1]

    # Prepare new content
    new_content = before_marker + start_marker

    # Handle opening div tag
    if analysis['has_opening_div']:
        div_match = re.match(r'(\s*<div align="justify">\s*)', after_marker)
        if div_match:
            opening_div = div_match.group(1)
            new_content += opening_div
            after_marker = after_marker[len(opening_div):]
        else:
            new_content += "\n<div align=\"justify\">\n"
    else:
        new_content += "\n<div align=\"justify\">\n"

    # Add all articles in correct order
    for article in all_articles:
        new_content += article['entry'] + "\n"

    # Add the rest of the content
    if analysis['has_end_marker']:
        end_idx = after_marker.find("<!-- ARTICOL CATEGORIE FINAL -->")
        if end_idx != -1:
            new_content += after_marker[end_idx:]
        else:
            new_content += after_marker
    else:
        new_content += after_marker

    # Write the updated content back to the file
    return write_file_with_encoding(category_file_path, new_content)

def extract_existing_articles(content):
    """Extract all existing articles with their dates from category content."""
    articles = []

    # Split content into individual articles
    article_blocks = re.split(r'(<table width="\d+" border="0">.*?</table>\s*<p class="text_obisnuit2">.*?</p>\s*<table width="552" border="0">.*?</table>\s*<p class="text_obisnuit">\s*</p>)',
                             content, flags=re.DOTALL)

    # Filter out empty strings and non-article blocks
    article_blocks = [block for block in article_blocks if block.strip() and '<table width=' in block]

    for block in article_blocks:
        # Extract date
        date_match = re.search(r'On (.*?), in <a href="[^"]+" title="[^"]+" class="[^"]+" rel="[^"]+">[^<]+</a>, by Neculai Fantanaru', block)
        if not date_match:
            continue

        date_str = date_match.group(1)
        try:
            # Parse date
            if ',' in date_str:
                # English date format "February 28, 2022"
                date_obj = datetime.strptime(date_str, '%B %d, %Y')
            else:
                # Romanian date format "Decembrie 31, 2024"
                months_ro = {
                    'ianuarie': 1, 'februarie': 2, 'martie': 3, 'aprilie': 4,
                    'mai': 5, 'iunie': 6, 'iulie': 7, 'august': 8,
                    'septembrie': 9, 'octombrie': 10, 'noiembrie': 11, 'decembrie': 12
                }
                month_day, year = date_str.split(', ')
                month_ro, day = month_day.split(' ')
                month = months_ro.get(month_ro.lower(), 1)
                date_obj = datetime(int(year), month, int(day))

            articles.append({
                'date': date_obj,
                'entry': block
            })
        except Exception as e:
            print(f"  [Error] Could not parse date '{date_str}': {str(e)}")
            continue

    return articles

def update_index_file(index_file_path, all_articles):
    """Update the index.html file with recent articles (last 4 months)."""
    print(f"\nUpdating index file: {index_file_path}")

    # Read index file
    content = read_file_with_fallback_encoding(index_file_path)
    if not content:
        print(f"  [Error] Could not read index file")
        return False

    # Fix special characters
    content = fix_special_characters(content)

    # Extract existing URLs to avoid duplicates
    existing_urls = extract_existing_urls(content)
    print(f"  [Debug] Found {len(existing_urls)} existing URLs in index file")

    # Current date for comparison (4 months ago)
    current_date = datetime.now()
    four_months_ago = current_date - timedelta(days=120)  # Approximately 4 months
    print(f"  [Debug] Current date: {current_date.strftime('%Y-%m-%d')}")
    print(f"  [Debug] Four months ago: {four_months_ago.strftime('%Y-%m-%d')}")

    # Filter recent articles (last 4 months)
    recent_articles = []
    for article in all_articles:
        # Skip if already in index
        if article['article_url'] in existing_urls:
            print(f"  [Info] Article already in index: {article['article_url']}")
            continue

        # Check if article is recent (within last 4 months)
        if article['datetime'] >= four_months_ago:
            recent_articles.append(article)
            print(f"  [Debug] Recent article found: {article['title']} ({article['date']})")

    # If no recent articles, skip
    if not recent_articles:
        print(f"  [Info] No recent articles to add to index")
        return True

    # Sort recent articles by date (oldest first - ascending order)
    sorted_articles = sorted(recent_articles, key=lambda x: x['sort_key'])
    print(f"  [Debug] Found {len(sorted_articles)} recent articles to add to index")

    # Find insertion point in index file
    # Look for the exact pattern: <!-- ARTICOL CATEGORIE START --> followed by <div align="justify">
    insertion_pattern = r'(<!-- ARTICOL CATEGORIE START -->\s*<div align="justify">)'
    match = re.search(insertion_pattern, content)
    if not match:
        print(f"  [Error] Could not find insertion point in index file")
        return False

    insertion_point = match.end()

    # Prepare article entries HTML
    articles_html = ""
    for article in sorted_articles:
        entry = create_new_article_entry(article)
        articles_html += entry + "\n"

    # Insert articles at the right position - immediately after <div align="justify">
    new_content = content[:insertion_point] + "\n" + articles_html + content[insertion_point:]

    # Write updated content
    return write_file_with_encoding(index_file_path, new_content)

def backup_all_files(target_dir, processed_category_files, output_dir, backup_dir):
    """Backup both processed target HTML files and original output HTML files to a backup directory."""
    print("\nStep 5: Backing up all processed files...")
    print("=" * 60)

    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        try:
            os.makedirs(backup_dir)
            print(f"  [Info] Created backup directory: {backup_dir}")
        except Exception as e:
            print(f"  [Error] Failed to create backup directory: {str(e)}")
            return False

    # Part 1: Copy the modified files from target directory
    backed_up_target = 0
    target_errors = 0

    # Copy index.html first
    index_file = os.path.join(target_dir, "index.html")
    if os.path.exists(index_file):
        try:
            shutil.copy2(index_file, os.path.join(backup_dir, "index.html"))
            backed_up_target += 1
            print(f"  [Success] Backed up target file: index.html")
        except Exception as e:
            target_errors += 1
            print(f"  [Error] Failed to backup index.html: {str(e)}")

    # Copy all category files that were processed
    for category_file in processed_category_files:
        source_path = os.path.join(target_dir, category_file)
        dest_path = os.path.join(backup_dir, category_file)

        try:
            # Create subdirectories in backup if needed
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(source_path, dest_path)
            backed_up_target += 1
            print(f"  [Success] Backed up target file: {category_file}")
        except Exception as e:
            target_errors += 1
            print(f"  [Error] Failed to backup target file {category_file}: {str(e)}")

    # Part 2: Copy all original HTML files from output directory
    backed_up_output = 0
    output_errors = 0

    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            if filename.endswith('.html'):
                source_path = os.path.join(output_dir, filename)
                dest_path = os.path.join(backup_dir, filename)

                try:
                    shutil.copy2(source_path, dest_path)
                    backed_up_output += 1
                    print(f"  [Success] Backed up output file: {filename}")
                except Exception as e:
                    output_errors += 1
                    print(f"  [Error] Failed to backup output file {filename}: {str(e)}")
    else:
        print(f"  [Error] Output directory does not exist: {output_dir}")

    print("\nBackup summary:")
    print(f"- Target files backed up: {backed_up_target}")
    print(f"- Target backup errors: {target_errors}")
    print(f"- Output files backed up: {backed_up_output}")
    print(f"- Output backup errors: {output_errors}")
    print(f"- Total files backed up: {backed_up_target + backed_up_output}")
    print("=" * 60)

    return (backed_up_target + backed_up_output) > 0

def process_articles():
    """Process all article files from output directory and update category files."""
    output_dir = r"e:\Carte\BB\17 - Site Leadership\alte\Ionel Balauta\Aryeht\Task 1 - Traduce tot site-ul\Doar Google Web\Andreea\Meditatii\2023\Iulia Python\output"
    target_dir = r"e:\Carte\BB\17 - Site Leadership\Principal\en"
    index_file = os.path.join(target_dir, "index.html")
    backup_dir = r"c:\Folder1\fisiere_html"

    if not os.path.exists(output_dir):
        print(f"ERROR: Output directory does not exist: {output_dir}")
        return

    if not os.path.exists(target_dir):
        print(f"ERROR: Target directory does not exist: {target_dir}")
        return

    print("\nStarting article processing...")
    print("=" * 60)

    # Organize articles by category
    articles_by_category = {}

    # Store all article info for later index.html update
    all_articles = []

    # Keep track of processed category files for backup
    processed_category_files = set()

    # Keep track of processed article files for copying
    processed_article_files = []

    # Process all articles first
    for filename in os.listdir(output_dir):
        if not filename.endswith('.html'):
            continue

        article_path = os.path.join(output_dir, filename)

        print(f"Processing article: {filename}")
        article_content = read_file_with_fallback_encoding(article_path)

        if not article_content:
            print(f"  [Error] Could not read article file: {filename}")
            continue

        # Extract article information
        article_info = extract_article_info(article_content)
        if not article_info:
            print(f"  [Error] Could not extract article information from: {filename}")
            continue

        # Get category filename
        category_filename = extract_category_filename(article_info['category_link'])
        if not category_filename:
            print(f"  [Error] Could not extract category filename from link: {article_info['category_link']}")
            continue

        # Add to the set of processed category files
        processed_category_files.add(category_filename)

        # Add to list of articles to be copied
        processed_article_files.append((article_path, os.path.join(target_dir, filename)))

        # Organize articles by category
        if category_filename not in articles_by_category:
            articles_by_category[category_filename] = {}

        # Organize articles by year within each category
        year = article_info['year']
        if year not in articles_by_category[category_filename]:
            articles_by_category[category_filename][year] = []

        # Add article - we store the entire article_info for later use
        articles_by_category[category_filename][year].append({
            'url': article_info['article_url'],
            'info': article_info  # Keep the original info for later use
        })

        # Add to all articles list for index.html update
        all_articles.append(article_info)

    # Now update each category file
    processed_categories = 0
    success_categories = 0
    error_categories = 0

    for category_filename, article_entries_by_year in articles_by_category.items():
        processed_categories += 1
        print(f"Updating category: {category_filename}")

        # Build path to category file
        category_path = os.path.join(target_dir, category_filename)
        if not os.path.exists(category_path):
            print(f"  [Error] Category file does not exist: {category_path}")
            error_categories += 1
            continue

        # Update category file
        if update_category_file(category_path, article_entries_by_year):
            print(f"  [Success] Updated category file: {category_filename}")
            success_categories += 1
        else:
            print(f"  [Error] Failed to update category file: {category_filename}")
            error_categories += 1

        print("")  # Add an empty line for better readability

    # Step 4: Copy processed articles from output to target directory
    print("\nStep 4: Copying processed articles to target directory...")
    print("=" * 60)
    copied_articles = 0
    copy_errors = 0

    for src_path, dest_path in processed_article_files:
        try:
            shutil.copy2(src_path, dest_path)
            copied_articles += 1
            print(f"  [Success] Copied {os.path.basename(src_path)} to target directory")
        except Exception as e:
            copy_errors += 1
            print(f"  [Error] Failed to copy {os.path.basename(src_path)}: {str(e)}")

    print(f"\nCopied {copied_articles} articles to target directory")
    print(f"Copy errors: {copy_errors}")
    print("=" * 60)

    # Update index.html with recent articles
    index_updated = False
    if os.path.exists(index_file):
        index_updated = update_index_file(index_file, all_articles)
    else:
        print(f"ERROR: Index file does not exist: {index_file}")

    print("=" * 60)
    print("Final report:")
    print(f"- Total categories processed: {processed_categories}")
    print(f"- Successfully updated: {success_categories}")
    print(f"- Categories with errors: {error_categories}")
    print(f"- Articles copied to target: {copied_articles}")
    print(f"- Copy errors: {copy_errors}")
    print(f"- Index.html updated: {'Yes' if index_updated else 'No'}")
    print("=" * 60)

    # Step 5: Backup all processed files
    backup_all_files(target_dir, processed_category_files, output_dir, backup_dir)

    print("Processing complete!")

if __name__ == "__main__":
    process_articles()