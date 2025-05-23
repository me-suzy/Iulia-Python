import os
import re
import shutil
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Track processing start time
START_TIME = datetime.now()

# Configuration
DEBUG = True
OUTPUT_DIR = r"e:\Carte\BB\17 - Site Leadership\alte\Ionel Balauta\Aryeht\Task 1 - Traduce tot site-ul\Doar Google Web\Andreea\Meditatii\2023\Iulia Python\output"
EN_DIR = r"e:\Carte\BB\17 - Site Leadership\Principal\en"
RO_DIR = r"e:\Carte\BB\17 - Site Leadership\Principal\ro"
BACKUP_DIR = r"c:\Folder1\fisiere_html"

def log(message):
    if DEBUG:
        print(message)

def read_file_with_fallback(file_path):
    encodings = ['utf-8', 'latin1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    log(f"[ERROR] Failed to read {file_path}")
    return None

def extract_article_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract title
    title_tag = soup.find('h1', class_='den_articol')
    if not title_tag:
        return None
    title = title_tag.get_text().strip()

    # Extract canonical URL
    canonical = soup.find('link', rel='canonical')
    if not canonical:
        return None
    url = canonical.get('href', '').strip()

    # Extract date and category
    meta_tag = soup.find('td', class_='text_dreapta')
    if not meta_tag:
        return None

    # Date extraction
    date_match = re.search(r'On (.*?),', meta_tag.get_text())
    if not date_match:
        return None
    date_str = date_match.group(1).strip()

    # Ensure date has year
    if not re.search(r'\d{4}$', date_str):
        date_str += f", {datetime.now().year}"

    # Category extraction
    category_tag = meta_tag.find('a')
    if not category_tag:
        return None
    category_url = category_tag.get('href', '').strip()
    category_name = category_tag.get_text().strip()

    # Extract RO link from flags
    ro_flag = soup.find('img', {'title': 'ro', 'alt': 'ro'})
    ro_link = ro_flag.parent.get('href', '').strip() if ro_flag else None

    # Extract quote
    quote_tag = soup.find('p', class_='text_obisnuit2')
    quote = quote_tag.get_text().strip() if quote_tag else None

    # Parse date for sorting
    try:
        if ',' in date_str:
            article_date = datetime.strptime(date_str, '%B %d, %Y')
        else:
            article_date = datetime.strptime(date_str, '%d %B %Y')
    except ValueError:
        article_date = datetime.now()

    return {
        'title': title,
        'url': url,
        'date': date_str,
        'category_url': category_url,
        'category_name': category_name,
        'ro_link': ro_link,
        'quote': quote,
        'date_obj': article_date,
        'sort_key': article_date.strftime('%Y%m%d')
    }

def generate_article_html(article):
    # Generate HTML for an article without extra newlines between segments
    return f"""    <table width="638" border="0">
        <tr>
          <td><span class="den_articol"><a href="{article['url']}" class="linkMare">{article['title']}</a></span></td>
        </tr>
        <tr>
          <td class="text_dreapta">On {article['date']}, in <a href="{article['category_url']}" title="View all articles from {article['category_name']}" class="external" rel="category tag">{article['category_name']}</a>, by Neculai Fantanaru</td>
        </tr>
      </table>
      <p class="text_obisnuit2"><em>{article['quote'] or 'True knowledge begins where you dare to transcend the limits imposed by the teachings of others.'}</em></p>
      <table width="552" border="0">
        <tr>
          <td width="552"><div align="right" id="external2"><a href="{article['url']}">read more </a><a href="https://neculaifantanaru.com/en/" title=""><img src="Arrow3_black_5x7.gif" alt="" width="5" height="7" class="arrow" /></a></div></td>
        </tr>
      </table>
      <p class="text_obisnuit"></p>"""

def update_category_file(category_path, articles):
    content = read_file_with_fallback(category_path)
    if not content:
        return False

    # Determine the category URL from the file name
    category_filename = os.path.basename(category_path)
    expected_category_url = f"https://neculaifantanaru.com/en/{category_filename}"

    # Extract the section between <!-- ARTICOL CATEGORIE START --> and <!-- ARTICOL CATEGORIE FINAL -->
    section_pattern = re.compile(r'<!-- ARTICOL CATEGORIE START -->.*?<!-- ARTICOL CATEGORIE FINAL -->', re.DOTALL)
    section_match = section_pattern.search(content)
    if not section_match:
        log(f"[ERROR] Nu s-a găsit secțiunea de articole în {category_filename}")
        return False

    section_content = section_match.group(0)

    # Find existing article URLs within the section
    existing_urls = set(re.findall(r'href="(https://neculaifantanaru\.com/en/[^"]+)"', section_content))

    # Filter new articles: only those that belong to this category and are not duplicates
    new_articles = [
        article for article in articles
        if article['category_url'] == expected_category_url and article['url'] not in existing_urls
    ]
    if not new_articles:
        log(f"[INFO] Niciun articol nou pentru categoria {category_filename}")
        return True

    # Find insertion point
    insert_pos = content.find('<!-- ARTICOL CATEGORIE START -->')
    if insert_pos == -1:
        log(f"[ERROR] Nu s-a găsit punctul de inserare în {category_filename}")
        return False
    insert_pos = content.find('<div align="justify">', insert_pos) + len('<div align="justify">')

    # Generate new content
    new_content = content[:insert_pos]
    for article in new_articles:
        new_content += '\n' + generate_article_html(article)
    new_content += content[insert_pos:]

    # Write updated file
    try:
        with open(category_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        log(f"[SUCCESS] Updated {category_filename} with {len(new_articles)} articles")
        return True
    except Exception as e:
        log(f"[ERROR] Failed to write {category_path}: {str(e)}")
        return False

def update_index_file(en_index_path, articles, ro_index_path):
    log(f"\nUpdating index file: {os.path.basename(en_index_path)}")

    # Read the current EN index content
    content = read_file_with_fallback(en_index_path)
    if not content:
        log("[ERROR] Failed to read EN index file")
        return False

    # Extract all existing article URLs to avoid duplicates
    existing_urls = set()
    for match in re.finditer(r'href="(https://neculaifantanaru\.com/en/[^"]+)"', content):
        existing_urls.add(match.group(1))
    log(f"[DEBUG] Found {len(existing_urls)} existing articles in index")

    # Read RO index if exists
    ro_content = ""
    if os.path.exists(ro_index_path):
        ro_content = read_file_with_fallback(ro_index_path) or ""
        log("[DEBUG] RO index content loaded")
    else:
        log("[WARNING] RO index file not found")

    # Filter articles - must be:
    # 1. Not already in index
    # 2. Have RO version if RO index exists
    # 3. From last 4 months
    four_months_ago = datetime.now() - timedelta(days=120)
    valid_articles = []

    for article in articles:
        if article['url'] in existing_urls:
            log(f"[SKIP] Articol deja existent in index: {article['title']}")
            continue

        if article['date_obj'] < four_months_ago:
            log(f"[SKIP] Article too old: {article['title']} ({article['date']})")
            continue

        if ro_content and article.get('ro_link'):
            ro_filename = os.path.basename(article['ro_link'].split('?')[0])
            if f'/{ro_filename}"' not in ro_content and f'/{ro_filename}?' not in ro_content:
                log(f"[SKIP] Missing RO version for: {article['title']}")
                continue

        valid_articles.append(article)

    if not valid_articles:
        log("[INFO] Niciun articol nou de adaugat")
        return True

    # Sort articles by date (ascending)
    valid_articles.sort(key=lambda x: x['date_obj'])

    # Find insertion point
    insert_match = re.search(r'<!-- ARTICOL CATEGORIE START -->\s*<div align="justify">', content)
    if not insert_match:
        log("[ERROR] Could not find insertion point in index")
        return False

    insert_pos = insert_match.end()

    # Build new content
    new_content = content[:insert_pos] + '\n'
    for article in valid_articles:
        new_content += generate_article_html(article)
    new_content += content[insert_pos:]

    # Write updated file
    try:
        with open(en_index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        log(f"[SUCCESS] Added {len(valid_articles)} articles to index")
        return True
    except Exception as e:
        log(f"[ERROR] Failed to write index: {str(e)}")
        return False

def main():
    # Verifică existența directorului OUTPUT_DIR
    if not os.path.exists(OUTPUT_DIR):
        log(f"[FATAL ERROR] Output directory not found: {OUTPUT_DIR}")
        return

    # Verifică drepturi de scriere în EN_DIR
    if not os.access(EN_DIR, os.W_OK):
        log(f"[FATAL ERROR] No write permissions in: {EN_DIR}")
        return

    log("="*60)
    log(f"Process started at {START_TIME}")
    log("STARTING ARTICLE PROCESSING")
    log("="*60)

    # Process all articles
    articles = []
    categories = set()
    modified_files = set()

    log("\nSTEP 1: Processing articles...")
    for filename in os.listdir(OUTPUT_DIR):
        if not filename.endswith('.html'):
            continue

        filepath = os.path.join(OUTPUT_DIR, filename)
        content = read_file_with_fallback(filepath)
        if not content:
            continue

        article = extract_article_data(content)
        if article:
            articles.append(article)
            categories.add(article['category_url'])

            # Copy to EN directory
            en_path = os.path.join(EN_DIR, filename)
            shutil.copy2(filepath, en_path)
            modified_files.add(en_path)
            log(f"[COPY] {filename} -> {en_path}")

    log("\n" + "="*60)
    log("PROCESSING COMPLETE")
    log(f"Processed articles: {len(articles)}")
    log(f"Updated categories: {len(categories)}")
    log(f"Total processing time: {datetime.now() - START_TIME}")
    log("="*60)

    if not articles:
        log("[ERROR] No articles processed")
        return

    log("\nSTEP 2: Updating category files...")
    for category_url in categories:
        category_file = os.path.basename(category_url)
        category_path = os.path.join(EN_DIR, category_file)
        if os.path.exists(category_path):
            if update_category_file(category_path, articles):
                modified_files.add(category_path)

    log("\nSTEP 3: Updating EN index...")
    en_index = os.path.join(EN_DIR, 'index.html')
    ro_index = os.path.join(RO_DIR, 'index.html')
    if update_index_file(en_index, articles, ro_index):
        modified_files.add(en_index)

    log("\nSTEP 4: Creating backup...")
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        backed_up = 0

        for filepath in modified_files:
            if os.path.exists(filepath):
                dest = os.path.join(BACKUP_DIR, os.path.basename(filepath))
                shutil.copy2(filepath, dest)
                log(f"[BACKUP] {os.path.basename(filepath)}")
                backed_up += 1

        if backed_up > 0:
            log(f"[SUCCESS] Backed up {backed_up} files to {BACKUP_DIR}")
        else:
            log("[INFO] No files needed backup")

    except Exception as e:
        log(f"[ERROR] Backup failed: {str(e)}")

    log("\n" + "="*60)
    log("FINAL PROCESSING REPORT")
    log(f"Total articles processed: {len(articles)}")
    log(f"Categories updated: {len(categories)}")
    log(f"Files backed up: {len(modified_files)}")
    log(f"Total processing time: {datetime.now() - START_TIME}")
    log("="*60)

if __name__ == "__main__":
    main()