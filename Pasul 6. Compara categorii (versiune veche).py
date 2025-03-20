import os
import re

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

def get_links_from_flags(content, filename, directory):  # Am adăugat parametrul directory
    """Extrage link-urile RO și EN din secțiunea FLAGS"""
    flags_section = re.search(r'<!-- FLAGS_1 -->(.*?)<!-- FLAGS -->', content, re.DOTALL)

    if not flags_section:
        print(f"\nFIȘIER PROBLEMATIC: {os.path.join(directory, filename)}")
        print("--------------------------------------------------")
        print("- Nu s-a găsit secțiunea FLAGS completă")
        return None

    flags_content = flags_section.group(1)

    # Caută link-ul RO (cu title="ro")
    ro_match = re.search(r'<a href="https://neculaifantanaru\.com/+([^"]+)"[^>]*?><img[^>]*?title="ro"', flags_content)

    # Caută link-ul EN (cu title="en")
    en_match = re.search(r'<a href="https://neculaifantanaru\.com/+en/([^"]+)"[^>]*?><img[^>]*?title="en"', flags_content)

    if not ro_match or not en_match:
        print(f"\nFIȘIER PROBLEMATIC: {os.path.join(directory, filename)}")
        print("--------------------------------------------------")
        print("Probleme găsite:")
        if not ro_match:
            print("  - Nu am găsit link-ul RO")
            ro_line = re.search(r'<a[^>]*title="ro".*?</a>', flags_content)
            if ro_line:
                print(f"  Link RO găsit: {ro_line.group(0)}")
        if not en_match:
            print("  - Nu am găsit link-ul EN")
            en_line = re.search(r'<a[^>]*title="en".*?</a>', flags_content)
            if en_line:
                print(f"  Link EN găsit: {en_line.group(0)}")
        print("--------------------------------------------------")
        return None

    return {
        'ro_link': ro_match.group(1),
        'en_link': en_match.group(1)
    }

def compare_files():
    mismatches = []

    for ro_file in os.listdir(ro_directory):
        if not ro_file.endswith('.html'):
            continue

        ro_path = os.path.join(ro_directory, ro_file)
        ro_content = read_file_with_fallback_encoding(ro_path)

        if not ro_content:
            continue

        ro_links = get_links_from_flags(ro_content, ro_file, ro_directory)  # Am adăugat ro_directory
        if not ro_links:
            continue

        # Construiește calea către fișierul EN
        en_file = ro_links['en_link']
        en_path = os.path.join(en_directory, en_file)

        if os.path.exists(en_path):
            en_content = read_file_with_fallback_encoding(en_path)
            if not en_content:
                continue

            en_links = get_links_from_flags(en_content, en_file, en_directory)  # Am adăugat en_directory
            if not en_links:
                continue

            # Verifică dacă link-urile diferă
            if ro_links != en_links:
                mismatches.append({
                    'ro_file': ro_file,
                    'en_file': en_file,
                    'ro_links': ro_links,
                    'en_links': en_links
                })

    return mismatches

# Rulează comparația
print("\nVerificare link-uri în FLAGS...")
mismatches = compare_files()

if mismatches:  # Adăugăm verificare dacă mismatches nu este None
   print("\nFișiere cu link-uri diferite între RO și EN:")
   print("-" * 80)

   for m in mismatches:
       # print(f"\nFișier RO: {m['ro_file']}")
       # print(f"Fișier EN: {m['en_file']}")
       print("\nÎn fișierul RO:")
       print(f"  Link RO: {m['ro_links']['ro_link']}")
       print(f"  Link EN: {m['ro_links']['en_link']}")
       print("\nÎn fișierul EN:")
       print(f"  Link RO: {m['en_links']['ro_link']}")
       print(f"  Link EN: {m['en_links']['en_link']}")
       print("-" * 80)

   print(f"\nTotal fișiere cu diferențe: {len(mismatches)}")
else:
   print("Nu s-au găsit diferențe între fișiere.")