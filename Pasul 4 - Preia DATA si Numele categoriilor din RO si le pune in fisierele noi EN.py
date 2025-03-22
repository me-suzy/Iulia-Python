import os
import re
from pathlib import Path

def translate_month(date_str):
    """Translate month from Romanian to English."""
    ro_to_en = {
        'Ianuarie': 'January',
        'Februarie': 'February',
        'Martie': 'March',
        'Aprilie': 'April',
        'Mai': 'May',
        'Iunie': 'June',
        'Iulie': 'July',
        'August': 'August',
        'Septembrie': 'September',
        'Octombrie': 'October',
        'Noiembrie': 'November',
        'Decembrie': 'December'
    }

    # Make a copy of the original string
    translated_str = date_str

    # Replace each Romanian month name with its English equivalent
    for ro, en in ro_to_en.items():
        translated_str = re.sub(ro, en, translated_str, flags=re.IGNORECASE)

    return translated_str

def category_mapping():
    """Mapping between Romanian and English categories."""
    return {
        'principiile-conducerii': {
            'link': 'leadership-principles',
            'title': 'Leadership Principles'
        },
        'leadership-real': {
            'link': 'real-leadership',
            'title': 'Real Leadership'
        },
        'legile-conducerii': {
            'link': 'leadership-laws',
            'title': 'Leadership Laws'
        },
        'dezvoltare-personala': {
            'link': 'personal-development',
            'title': 'Personal Development'
        },
        'leadership-de-succes': {
            'link': 'successful-leadership',
            'title': 'Successful Leadership'
        },
        'lideri-si-atitudine': {
            'link': 'leadership-and-attitude',
            'title': 'Leadership and Attitude'
        },
        'aptitudini-si-abilitati-de-leadership': {
            'link': 'leadership-skills-and-abilities',
            'title': 'Leadership Skills And Abilities'
        },
        'hr-resurse-umane': {
            'link': 'hr-human-resources',
            'title': 'Human Resources'
        },
        'leadership-total': {
            'link': 'total-leadership',
            'title': 'Total Leadership'
        },
        'leadership-de-durata': {
            'link': 'leadership-that-lasts',
            'title': 'Leadership That Lasts'
        },
        'calitatile-unui-lider': {
            'link': 'qualities-of-a-leader',
            'title': 'Qualities of A Leader'
        },
        'leadership-de-varf': {
            'link': 'top-leadership',
            'title': 'Top Leadership'
        },
        'jurnal-de-leadership': {
            'link': 'leadership-journal',
            'title': 'Leadership Journal'
        },
        'leadership-magic': {
            'link': 'leadership-magic',
            'title': 'Leadership Magic'
        }
    }

def read_file_with_fallback_encoding(file_path):
    """Read file using various encodings to handle diacritics."""
    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    content = None

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                print(f"  [Debug] File read with encoding: {encoding}")
                break
        except UnicodeDecodeError:
            print(f"  [Debug] Error reading with encoding: {encoding}")
            continue

    if content is None:
        print(f"ERROR: Could not read file {file_path} with any available encoding.")

    return content

def extract_item_id(content):
    """Extract article ID from HTML content."""
    patterns = [
        r'<!-- \$item_id = (\d+); // .*? -->',
        r'<!-- item_id = (\d+); -->',
        r'<!-- id: (\d+) -->'
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1)

    return None

def extract_ro_link_from_flags(content):
    """Extract Romanian link from the FLAGS section."""
    # Look for the entire FLAGS section
    flag_section = re.search(r'<!-- FLAGS_1 -->(.*?)<!-- FLAGS -->', content, re.DOTALL)
    if not flag_section:
        return None

    flags = flag_section.group(1)

    # Look for the Romanian link
    ro_match = re.search(r'<a href="https://neculaifantanaru\.com/([^"]+)"[^>]*?><img[^>]*?title="ro"', flags)
    if ro_match:
        return ro_match.group(1)

    return None

def extract_filename_from_path(file_path):
    """Extract the filename from a path, without extension."""
    basename = os.path.basename(file_path)
    filename = os.path.splitext(basename)[0]
    return filename

def find_matching_ro_file(en_filename, ro_files_by_id, ro_files_by_name, ro_dir):
    """Find matching Romanian file using multiple methods."""
    # Method 1: Try to match by ID
    if en_filename in ro_files_by_id:
        return ro_files_by_id[en_filename]

    # Method 2: Try direct filename match
    if en_filename in ro_files_by_name:
        ro_path = os.path.join(ro_dir, f"{en_filename}.html")
        if os.path.exists(ro_path):
            content = read_file_with_fallback_encoding(ro_path)
            return {
                'path': ro_path,
                'filename': f"{en_filename}.html",
                'content': content
            }

    return None

def extract_category_info(content):
    """Extract category information from Romanian file."""
    if not content:
        return None

    # Look for text_dreapta section
    pattern = r'<td class="text_dreapta">(.*?)</td>'
    text_section = re.search(pattern, content, re.DOTALL)
    if not text_section:
        print("  [Debug] The text_dreapta section not found")
        return None

    text_content = text_section.group(1)

    # Extract date - adjust the pattern to be more flexible
    date_pattern = r'On (.*?), in'
    date_match = re.search(date_pattern, text_content)
    if not date_match:
        print("  [Debug] Date not found in text_dreapta")
        return None

    date = date_match.group(1).strip()

    # Extract category
    category_pattern = r'<a href="https://neculaifantanaru\.com/([^"]+)" title="[^"]*" class="[^"]*"[^>]*>(.*?)</a>'
    category_match = re.search(category_pattern, text_content)
    if not category_match:
        category_pattern = r'<a href="https://neculaifantanaru\.com/([^"]+)"[^>]*>(.*?)</a>'
        category_match = re.search(category_pattern, text_content)
        if not category_match:
            print("  [Debug] Category link not found in text_dreapta")
            return None

    category_link = category_match.group(1)
    category_title = category_match.group(2).strip()

    # Remove .html extension
    if category_link.endswith('.html'):
        category_link = category_link[:-5]

    # Remove 'ro/' prefix if present
    if category_link.startswith('ro/'):
        category_link = category_link[3:]

    # Extract the category part from the link
    # For example, 'leadership-magic/some-article.html' -> 'leadership-magic'
    category_parts = category_link.split('/')
    if len(category_parts) > 1:
        category_link = category_parts[0]

    # Look up in mapping
    mapping = category_mapping()
    if category_link in mapping:
        en_link = mapping[category_link]['link']
        en_title = mapping[category_link]['title']
    else:
        # If not in mapping, use the same values
        print(f"  [Warning] Category '{category_link}' not found in mapping. Using the same value.")
        en_link = category_link
        en_title = category_title

    # Ensure the date has English month names
    translated_date = translate_month(date)

    return {
        'date': translated_date,
        'ro_category_link': category_link,
        'ro_category_title': category_title,
        'en_category_link': en_link,
        'en_category_title': en_title
    }

def update_en_file_category(en_content, category_info):
    """Update category and date information in the EN file."""
    if not en_content or not category_info:
        return en_content

    # Build new text_dreapta section
    new_text = f'On {category_info["date"]}, in <a href="https://neculaifantanaru.com/en/{category_info["en_category_link"]}.html" title="View all articles from {category_info["en_category_title"]}" class="external" rel="category tag">{category_info["en_category_title"]}</a>, by Neculai Fantanaru'

    # Replace old section
    pattern = r'<td class="text_dreapta">(.*?)</td>'
    updated_content = re.sub(pattern, f'<td class="text_dreapta">{new_text}</td>', en_content, count=1, flags=re.DOTALL)

    return updated_content

def process_files():
    """Process all files to update categories and dates."""
    output_dir = r"e:\Carte\BB\17 - Site Leadership\alte\Ionel Balauta\Aryeht\Task 1 - Traduce tot site-ul\Doar Google Web\Andreea\Meditatii\2023\Iulia Python\output"
    ro_dir = r"e:\Carte\BB\17 - Site Leadership\Principal\ro"

    if not os.path.exists(output_dir):
        print(f"ERROR: Output directory does not exist: {output_dir}")
        return

    if not os.path.exists(ro_dir):
        print(f"ERROR: RO directory does not exist: {ro_dir}")
        return

    print("\nStarting file processing...")
    print("=" * 60)

    # Index Romanian files by ID and filename for quick reference
    ro_files_by_id = {}
    ro_files_by_name = {}
    ro_files_count = 0

    print(f"Indexing files from Romanian directory: {ro_dir}")
    for filename in os.listdir(ro_dir):
        if not filename.endswith('.html'):
            continue

        ro_files_count += 1
        file_path = os.path.join(ro_dir, filename)
        content = read_file_with_fallback_encoding(file_path)

        if content:
            # Index by ID
            item_id = extract_item_id(content)
            if item_id:
                ro_files_by_id[item_id] = {
                    'path': file_path,
                    'filename': filename,
                    'content': content
                }

            # Index by filename without extension
            base_filename = os.path.splitext(filename)[0]
            ro_files_by_name[base_filename] = {
                'path': file_path,
                'filename': filename,
                'content': content
            }

    print(f"Indexed {len(ro_files_by_id)} files by ID from {ro_files_count} Romanian files")
    print(f"Indexed {len(ro_files_by_name)} files by name from {ro_files_count} Romanian files\n")

    # Process files from output directory
    output_files_count = 0
    updated_files_count = 0
    error_files_count = 0

    for filename in os.listdir(output_dir):
        if not filename.endswith('.html'):
            continue

        output_files_count += 1
        file_path = os.path.join(output_dir, filename)
        base_filename = os.path.splitext(filename)[0]

        print(f"Processing file: {filename}")
        content = read_file_with_fallback_encoding(file_path)

        if not content:
            print(f"  ERROR: Could not read file {filename}. Continuing with next file.")
            error_files_count += 1
            continue

        # Method 1: Direct filename match
        ro_file = None
        if base_filename in ro_files_by_name:
            ro_file = ro_files_by_name[base_filename]
            print(f"  Found Romanian file by name: {ro_file['filename']}")

        # Method 2: Extract ID and match
        if not ro_file:
            item_id = extract_item_id(content)
            if item_id and item_id in ro_files_by_id:
                ro_file = ro_files_by_id[item_id]
                print(f"  Found Romanian file by ID ({item_id}): {ro_file['filename']}")

        # Method 3: Extract Romanian link from FLAGS
        if not ro_file:
            ro_link = extract_ro_link_from_flags(content)
            if ro_link:
                print(f"  Romanian link found in FLAGS: {ro_link}")

                # Build path to Romanian file
                if not ro_link.endswith('.html'):
                    ro_link += '.html'

                # Extract just the filename part
                ro_filename = os.path.basename(ro_link)
                ro_path = os.path.join(ro_dir, ro_filename)

                if os.path.exists(ro_path):
                    ro_content = read_file_with_fallback_encoding(ro_path)
                    if ro_content:
                        ro_file = {
                            'path': ro_path,
                            'filename': ro_filename,
                            'content': ro_content
                        }
                        print(f"  Found Romanian file by link: {ro_filename}")

        # If no Romanian file found, skip
        if not ro_file:
            print(f"  WARNING: No matching Romanian file found for {filename}")
            error_files_count += 1
            continue

        # Extract category info from Romanian file
        category_info = extract_category_info(ro_file['content'])

        if not category_info:
            print(f"  WARNING: Could not extract category info from Romanian file {ro_file['filename']}")
            error_files_count += 1
            continue

        print(f"  Category info found:")
        print(f"    - Date: {category_info['date']}")
        print(f"    - RO Category: {category_info['ro_category_title']} ({category_info['ro_category_link']})")
        print(f"    - EN Category: {category_info['en_category_title']} ({category_info['en_category_link']})")

        # Update EN file
        updated_content = update_en_file_category(content, category_info)

        # Save updated file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            updated_files_count += 1
            print(f"  File successfully updated!")
        except Exception as e:
            print(f"  ERROR: Could not save file {filename}: {str(e)}")
            error_files_count += 1

        print("\n")

    print("=" * 60)
    print("Final report:")
    print(f"- Total files in output directory: {output_files_count}")
    print(f"- Successfully updated files: {updated_files_count}")
    print(f"- Files with errors: {error_files_count}")
    print("=" * 60)
    print("Processing complete!")

if __name__ == "__main__":
    process_files()