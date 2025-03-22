import os
import re
from pathlib import Path

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

def normalize_value(val):
    if val is None:
        return None
    val = val.replace('\xa0', ' ').strip().lower()
    val = val.replace('–', '-').replace('—', '-')
    return val

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

    for ro_file in os.listdir(ro_directory):
        if not ro_file.endswith('.html'):
            continue

        print(f"Procesare fișier: {ro_file}", flush=True)
        ro_path = os.path.join(ro_directory, ro_file)
        ro_content = read_file_with_fallback_encoding(ro_path)
        if not ro_content:
            continue

        ro_links = get_links_from_flags(ro_content, ro_file, ro_directory)
        if not ro_links:
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
        if not en_links:
            continue

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