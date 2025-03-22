import os
import re
from pathlib import Path
from unidecode import unidecode

ro_directory = r'e:\Carte\BB\17 - Site Leadership\Principal\ro'
en_directory = r'e:\Carte\BB\17 - Site Leadership\Principal\en'

def read_file_with_fallback_encoding(file_path):
    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    print(f"Nu s-a putut citi fișierul {file_path}")
    return None

def replace_special_chars(val):
    val = val.replace('–', '-').replace('—', '-')
    return val

def normalize_value(val):
    if val is None:
        return None
    val = val.replace('\xa0', ' ').strip().lower()
    val = replace_special_chars(val)
    return val

def translate_month(date_str):
    ro_to_en = {
        'Ianuarie': 'January', 'Februarie': 'February', 'Martie': 'March',
        'Aprilie': 'April', 'Mai': 'May', 'Iunie': 'June', 'Iulie': 'July',
        'August': 'August', 'Septembrie': 'September', 'Octombrie': 'October',
        'Noiembrie': 'November', 'Decembrie': 'December'
    }
    date_str = date_str.lower()
    for ro, en in ro_to_en.items():
        if ro.lower() in date_str:
            return date_str.replace(ro.lower(), en.lower())
    return date_str

def normalize_date(date_str):
    return ' '.join(date_str.split()).replace(',', '')

def get_category_mapping():
    return {
        'principiile-conducerii': 'leadership-principles',
        'leadership-real': 'real-leadership',
        'legile-conducerii': 'leadership-laws',
        'dezvoltare-personala': 'personal-development',
        'leadership-de-succes': 'successful-leadership',
        'lideri-si-atitudine': 'leadership-and-attitude',
        'aptitudini-si-abilitati-de-leadership': 'leadership-skills-and-abilities',
        'hr-resurse-umane': 'hr-human-resources',
        'leadership-total': 'total-leadership',
        'leadership-de-durata': 'leadership-that-lasts',
        'calitatile-unui-lider': 'qualities-of-a-leader',
        'leadership-de-varf': 'top-leadership',
        'jurnal-de-leadership': 'leadership-journal',
        'leadership-magic': 'leadership-magic'
    }

def get_article_info(content, filename, directory):
    article_section = re.search(r'<!-- ARTICOL START -->(.*?)<\/table>', content, re.DOTALL)
    if not article_section:
        print(f"Nu s-a găsit secțiunea ARTICOL START în {os.path.join(directory, filename)}")
        return None

    article_content = article_section.group(1)
    date_match = re.search(r'On\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})', article_content, re.IGNORECASE)
    category_match = re.search(r'<a href="https://neculaifantanaru\.com(?:/en)?/([^"]+)"[^>]*>(.*?)</a>', article_content)

    if not date_match or not category_match:
        print(f"Probleme la extragerea datelor din {os.path.join(directory, filename)}")
        return None

    return {
        'date': normalize_date(translate_month(date_match.group(1))),
        'category_link': normalize_value(category_match.group(1)),
        'category_title': normalize_value(category_match.group(2))
    }

def get_links_from_flags(content, filename, directory):
    flags_section = re.search(r'<!-- FLAGS_1 -->(.*?)<!-- FLAGS -->', content, re.DOTALL)
    if not flags_section:
        print(f"\nFIȘIER PROBLEMATIC: {os.path.join(directory, filename)} - Nu s-a găsit secțiunea FLAGS")
        return None

    flags_content = flags_section.group(1)
    ro_match = re.search(r'<a href="https://neculaifantanaru\.com/+([^"]+)"[^>]*?><img[^>]*?title="ro"', flags_content)
    en_match = re.search(r'<a href="https://neculaifantanaru\.com/+en/([^"]+)"[^>]*?><img[^>]*?title="en"', flags_content)

    if not ro_match or not en_match:
        print(f"\nFIȘIER PROBLEMATIC: {os.path.join(directory, filename)} - Lipsesc link-urile RO/EN")
        return None

    return {
        'ro_link': normalize_value(ro_match.group(1)),
        'en_link': normalize_value(en_match.group(1))
    }

def compare_files():
    mismatches = []
    unique_mismatches = set()  # Pentru a elimina duplicatele
    category_map = get_category_mapping()

    for ro_file in os.listdir(ro_directory):
        if not ro_file.endswith('.html'):
            continue

        print(f"Procesare fișier: {ro_file}")
        ro_path = os.path.join(ro_directory, ro_file)
        ro_content = read_file_with_fallback_encoding(ro_path)
        if not ro_content:
            continue

        ro_links = get_links_from_flags(ro_content, ro_file, ro_directory)
        ro_article = get_article_info(ro_content, ro_file, ro_directory)
        if not ro_links or not ro_article:
            continue

        en_file = ro_links['en_link']
        en_path = os.path.join(en_directory, en_file)

        if not os.path.exists(en_path):
            print(f"Fișierul EN nu există: {en_path}")
            continue

        en_content = read_file_with_fallback_encoding(en_path)
        if not en_content:
            continue

        en_links = get_links_from_flags(en_content, en_file, en_directory)
        en_article = get_article_info(en_content, en_file, en_directory)
        if not en_links or not en_article:
            continue

        # Debug: Afișăm link-urile extrase
        print(f"DEBUG: RO file {ro_file} - RO Link: {ro_links['ro_link']}, EN Link: {ro_links['en_link']}")
        print(f"DEBUG: EN file {en_file} - RO Link: {en_links['ro_link']}, EN Link: {en_links['en_link']}")

        # Verificăm data și categoria, dar raportăm doar diferențele din FLAGS
        date_mismatch = ro_article['date'] != en_article['date']
        ro_cat = ro_article['category_link'].replace('.html', '')
        en_cat = en_article['category_link'].replace('.html', '')
        expected_en_cat = category_map.get(ro_cat, ro_cat)
        category_mismatch = expected_en_cat != en_cat

        if date_mismatch:
            print(f"DEBUG: Date mismatch in {ro_file}: RO={ro_article['date']}, EN={en_article['date']}")
        if category_mismatch:
            print(f"DEBUG: Category mismatch in {ro_file}: RO={ro_cat}, EN={en_cat}")

        # Raportăm doar nepotrivirile din FLAGS
        if ro_links['ro_link'] != en_links['ro_link']:
            mismatch_key = (ro_links['ro_link'], ro_links['en_link'])  # Cheie unică pentru deduplicare
            if mismatch_key not in unique_mismatches:
                unique_mismatches.add(mismatch_key)
                mismatches.append({
                    'ro_file': ro_file,
                    'ro_link': ro_links['ro_link'],
                    'en_link': ro_links['en_link']
                })
                print(f"DEBUG: Mismatch found - RO Link: {ro_links['ro_link']}, EN Link: {ro_links['en_link']}")

    return mismatches

# Rulează comparația
print("\nVerificare link-uri în FLAGS...")
mismatches = compare_files()

if mismatches:
    print("\nFișiere cu link-uri diferite între RO și EN:")
    print("-" * 80)
    for m in mismatches:
        print("\nÎn fișierul RO:")
        print(f"  Link RO: {m['ro_link']}")
        print(f"  Link EN: {m['en_link']}")
    print("-" * 80)
    print(f"\nTotal fișiere cu diferențe: {len(mismatches)}")
else:
    print("Nu s-au găsit diferențe între fișiere.")