import os
import re
from pathlib import Path

def extract_item_id(file_content):
    """Extrage ID-ul articolului din comentariul HTML."""
    patterns = [
        r'<!-- \$item_id = (\d+); // .*? -->',
        r'<!-- item_id = (\d+); -->',
        r'<!-- id: (\d+) -->'
    ]

    for pattern in patterns:
        match = re.search(pattern, file_content)
        if match:
            return match.group(1)
    return None

def extract_flags_section(file_content):
    """Extrage secțiunea FLAGS din conținutul fișierului."""
    pattern = r'<!-- FLAGS_1 -->(.*?)<!-- FLAGS -->'
    match = re.search(pattern, file_content, re.DOTALL)
    if match:
        return match.group(0), match.group(1)
    return None, None

def extract_language_link(flags_content, language):
    """Extrage link-ul specific unei limbi din secțiunea FLAGS."""
    # Pattern-uri multiple pentru a face față diferitelor formate
    patterns = []

    if language == 'ro':
        patterns = [
            r'<a href="https://neculaifantanaru\.com/([^"]+)"[^>]*?><img[^>]*?title="ro"[^>]*?></a>',
            r'<a href="https://neculaifantanaru\.com/([^"]+)"[^>]*?title="ro"[^>]*?><img[^>]*?></a>',
            r'<a href="https://neculaifantanaru\.com/([^"]+)"[^>]*?><img[^>]*?alt="ro"[^>]*?></a>'
        ]
    elif language == 'en':
        patterns = [
            r'<a href="https://neculaifantanaru\.com/en/([^"]+)"[^>]*?><img[^>]*?title="en"[^>]*?></a>',
            r'<a href="https://neculaifantanaru\.com/en/([^"]+)"[^>]*?title="en"[^>]*?><img[^>]*?></a>',
            r'<a href="https://neculaifantanaru\.com/en/([^"]+)"[^>]*?><img[^>]*?alt="en"[^>]*?></a>'
        ]

    # Încercăm toate pattern-urile
    for pattern in patterns:
        matches = re.finditer(pattern, flags_content)
        for match in matches:
            # Găsim întreaga secțiune <a>...</a>
            start_idx = match.start()
            end_text = flags_content[start_idx:]
            tag_end = end_text.find('</a>')
            if tag_end != -1:
                end_idx = start_idx + tag_end + 4
                return flags_content[start_idx:end_idx]

    # Căutare avansată pentru cazuri speciale
    # Această abordare caută tag-uri <a> care conțin atât URL-ul corect cât și text/imagini specifice limbii
    if language == 'ro':
        match = re.search(r'<a [^>]*?href="https://neculaifantanaru\.com/[^"]*?"[^>]*?>.*?flag_lang_ro\.jpg.*?</a>', flags_content, re.DOTALL)
        if match:
            return match.group(0)
    elif language == 'en':
        match = re.search(r'<a [^>]*?href="https://neculaifantanaru\.com/en/[^"]*?"[^>]*?>.*?flag_lang_en\.jpg.*?</a>', flags_content, re.DOTALL)
        if match:
            return match.group(0)

    return None

def extract_filename_from_url(url_tag, language):
    """Extrage numele fișierului din tag-ul URL."""
    if language == 'ro':
        pattern = r'href="https://neculaifantanaru\.com/([^"]+)"'
    else:  # 'en'
        pattern = r'href="https://neculaifantanaru\.com/en/([^"]+)"'

    match = re.search(pattern, url_tag)
    if match:
        return match.group(1)
    return None

def is_special_term(ro_filename, en_filename):
    """
    Determină dacă perechea de URL-uri conține un termen special/străin care ar trebui păstrat.
    """
    # Elimină extensia .html
    ro_base = os.path.splitext(ro_filename)[0]
    en_base = os.path.splitext(en_filename)[0]

    # Caz 1: URL-uri identice - clar un termen special
    if ro_base == en_base:
        return True

    # Caz 2: Termeni foarte scurți (un singur cuvânt) - posibil termen special
    ro_parts = ro_base.split('-')
    en_parts = en_base.split('-')

    # Lista de cuvinte de legătură - doar acestea sunt codificate explicit
    stop_words = ['a', 'an', 'the', 'and', 'or', 'but', 'if', 'when', 'while', 'as',
                  'in', 'on', 'at', 'of', 'to', 'for', 'with', 'by', 'about', 'against',
                  'before', 'after', 'during', 'without', 'through', 'throughout', 'within',
                  'is', 'are', 'was', 'were', 'be', 'been', 'being', 'am',
                  's', 'd', 't', 'll', 've', 're', 'm',
                  'si', 'sau', 'dar', 'daca', 'cand', 'ca', 'pe', 'la', 'de', 'cu', 'prin',
                  'pentru', 'fara', 'despre', 'inainte', 'dupa', 'in', 'din', 'spre',
                  'este', 'sunt', 'era', 'fi', 'fost', 'fiind', 'e']

    # Filtrăm cuvintele de legătură pentru a obține cuvintele de conținut
    ro_content = [w for w in ro_parts if w.lower() not in stop_words and len(w) > 2]
    en_content = [w for w in en_parts if w.lower() not in stop_words and len(w) > 2]

    # Cazul URL-urilor scurte, cu un singur cuvânt
    if len(ro_parts) == 1 and len(ro_parts[0]) < 10 and ro_parts[0].lower() not in stop_words:
        return True

    if len(en_parts) == 1 and len(en_parts[0]) < 10 and en_parts[0].lower() not in stop_words:
        return True

    # Caz special pentru hikmah/wisdom - ambele sunt scurte dar complet diferite
    # Dacă ambele URL-uri sunt simple și scurte (un singur cuvânt sau două), verificăm caracteristicile lor
    if len(ro_parts) <= 2 and len(en_parts) <= 2:
        # Detectăm caracteristici de termen străin în oricare dintre termeni
        for word in ro_parts + en_parts:
            # Verifică pentru caracteristici neobișnuite (litere rare în cuvinte europene standard)
            if ('k' in word.lower() and 'h' in word.lower()) or 'q' in word.lower() or word.lower().startswith('x'):
                return True

            # Verifică pentru modele de consoane specifice limbilor străine
            consonant_groups = ['kh', 'hk', 'mk', 'km', 'tz', 'zk', 'gh']
            if any(group in word.lower() for group in consonant_groups):
                return True

    # Caz 3: Verifică pentru termeni comuni dar cu terminații diferite (initium/initiation)
    # Extrage rădăcinile cuvintelor (primele 4 litere pentru cuvinte de minim 6 litere)
    ro_stems = [word[:4] for word in ro_parts if len(word) >= 6 and word.lower() not in stop_words]
    en_stems = [word[:4] for word in en_parts if len(word) >= 6 and word.lower() not in stop_words]

    common_stems = set(ro_stems) & set(en_stems)

    # Dacă avem o rădăcină comună dar URL-urile sunt diferite structural, probabil e un termen special
    if common_stems and abs(len(ro_parts) - len(en_parts)) > 3:
        # Verifică dacă rădăcina comună pare a fi un termen neobișnuit/străin
        for stem in common_stems:
            # Rădăcini care par latine, grecești sau străine (verifică terminații neobișnuite)
            matching_ro_words = [w for w in ro_parts if w.startswith(stem)]
            matching_en_words = [w for w in en_parts if w.startswith(stem)]

            for word in matching_ro_words + matching_en_words:
                # Verifică dacă cuvântul are caracteristici de termen străin
                if (word.endswith('um') or word.endswith('us') or word.endswith('is') or
                    word.endswith('ae') or word.endswith('os') or
                    ('k' in word and 'w' not in word)):  # Caracteristici neobișnuite pentru cuvinte românești
                    return True

    # Caz 4: Cazul special pentru URL-uri foarte diferite ca structură dar cu conținut similar
    # Filtrăm pentru cazuri precum "memoria-harenae" vs "harena-s-memory"

    # Diferență extremă în numărul de cuvinte de conținut
    if (len(ro_content) == 1 and len(en_content) >= 4) or (len(en_content) == 1 and len(ro_content) >= 4):
        return True

    # Prevenim cazul cu ID 346 care este o traducere normală dar cu structură diferită
    # Pentru o traducere normală, chiar dacă structura e diferită, numărul de cuvinte semnificative
    # nu ar trebui să difere prea mult
    if abs(len(ro_content) - len(en_content)) <= 2:
        return False

    # Cazul implicit - nu este un termen special
    return False

def update_flags_section(file_content, ro_link, en_link, special_term=False):
    """Actualizează secțiunea FLAGS cu noile link-uri."""
    # Extragem secțiunea FLAGS
    flags_section, flags_content = extract_flags_section(file_content)
    if not flags_section or not flags_content:
        return file_content, False

    # Facem o copie a conținutului original pentru a verifica dacă au fost făcute modificări
    original_flags_content = flags_content
    updated_flags_content = flags_content

    # Actualizăm link-ul RO, dacă este furnizat
    if ro_link:
        # Pattern-uri multiple pentru link-ul RO
        ro_patterns = [
            r'<a [^>]*?href="https://neculaifantanaru\.com/[^"]*?"[^>]*?>.*?flag_lang_ro\.jpg.*?</a>',
            r'<a [^>]*?title="ro"[^>]*?href="https://neculaifantanaru\.com/[^"]*?"[^>]*?>.*?</a>',
            r'<a [^>]*?href="https://neculaifantanaru\.com/[^"]*?"[^>]*?title="ro"[^>]*?>.*?</a>'
        ]

        for pattern in ro_patterns:
            match = re.search(pattern, updated_flags_content, re.DOTALL)
            if match:
                updated_flags_content = updated_flags_content.replace(match.group(0), ro_link)
                break

    # Actualizăm link-ul EN, dacă este furnizat și nu este un termen special
    if en_link and not special_term:
        # Pattern-uri multiple pentru link-ul EN
        en_patterns = [
            r'<a [^>]*?href="https://neculaifantanaru\.com/en/[^"]*?"[^>]*?>.*?flag_lang_en\.jpg.*?</a>',
            r'<a [^>]*?title="en"[^>]*?href="https://neculaifantanaru\.com/en/[^"]*?"[^>]*?>.*?</a>',
            r'<a [^>]*?href="https://neculaifantanaru\.com/en/[^"]*?"[^>]*?title="en"[^>]*?>.*?</a>'
        ]

        for pattern in en_patterns:
            match = re.search(pattern, updated_flags_content, re.DOTALL)
            if match:
                updated_flags_content = updated_flags_content.replace(match.group(0), en_link)
                break

    # Verificăm dacă s-au făcut modificări
    if original_flags_content == updated_flags_content:
        return file_content, False

    # Reconstruim secțiunea FLAGS
    updated_flags_section = f'<!-- FLAGS_1 -->{updated_flags_content}<!-- FLAGS -->'

    # Înlocuim secțiunea veche cu cea nouă
    return file_content.replace(flags_section, updated_flags_section), True

def process_files(ro_dir, output_dir):
    """Procesează toate fișierele și face schimbul de flags."""
    # Dicționare pentru a asocia ID-urile cu fișierele
    ro_files = {}
    output_files = {}
    special_terms = []

    # Indexăm fișierele RO după ID
    print("\nIndexare fișiere RO...")
    for filename in os.listdir(ro_dir):
        if not filename.endswith('.html'):
            continue

        file_path = os.path.join(ro_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                item_id = extract_item_id(content)
                if item_id:
                    ro_files[item_id] = {
                        'path': file_path,
                        'filename': filename,
                        'content': content
                    }
        except Exception as e:
            print(f"Eroare la citirea fișierului {filename}: {e}")

    # Indexăm fișierele OUTPUT după ID
    print(f"Indexare fișiere OUTPUT din {output_dir}...")
    output_file_count = 0
    for filename in os.listdir(output_dir):
        if not filename.endswith('.html'):
            continue

        file_path = os.path.join(output_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                item_id = extract_item_id(content)
                if item_id:
                    output_files[item_id] = {
                        'path': file_path,
                        'filename': filename,
                        'content': content
                    }
                    output_file_count += 1
        except Exception as e:
            print(f"Eroare la citirea fișierului {filename}: {e}")

    print(f"S-au găsit {len(ro_files)} fișiere RO și {output_file_count} fișiere OUTPUT cu ID-uri.")

    # Găsim perechile de fișiere și facem schimbul de flags
    print("\nProcesare perechi de fișiere...\n")
    processed_pairs = 0
    failed_pairs = 0

    for item_id, ro_file in ro_files.items():
        if item_id in output_files:
            output_file = output_files[item_id]

            # Afișăm informații despre perechea curentă
            print(f"Procesare pereche ID {item_id}:")
            print(f"  - RO: {ro_file['filename']}")
            print(f"  - EN: {output_file['filename']}")

            # Extragem secțiunile FLAGS
            ro_flags_section, ro_flags_content = extract_flags_section(ro_file['content'])
            output_flags_section, output_flags_content = extract_flags_section(output_file['content'])

            if not ro_flags_section or not output_flags_section:
                print(f"  - EȘEC: Nu s-a găsit secțiunea FLAGS în unul sau ambele fișiere. Se continuă.")
                failed_pairs += 1
                continue

            # Extragem link-urile specifice
            ro_link_in_ro = extract_language_link(ro_flags_content, 'ro')
            en_link_in_output = extract_language_link(output_flags_content, 'en')

            if not ro_link_in_ro:
                print(f"  - EȘEC: Nu s-a găsit link-ul RO în fișierul RO.")
                failed_pairs += 1
                continue

            if not en_link_in_output:
                print(f"  - EȘEC: Nu s-a găsit link-ul EN în fișierul OUTPUT.")
                failed_pairs += 1
                continue

            # Extragem numele fișierelor din link-uri
            ro_filename = extract_filename_from_url(ro_link_in_ro, 'ro')
            en_filename = extract_filename_from_url(en_link_in_output, 'en')

            if not ro_filename or not en_filename:
                print(f"  - EȘEC: Nu s-au putut extrage numele fișierelor din link-uri.")
                failed_pairs += 1
                continue

            # Verificăm dacă este un termen special
            is_special = is_special_term(ro_filename, en_filename)
            if is_special:
                special_terms.append({
                    'id': item_id,
                    'ro_file': ro_file['filename'],
                    'en_file': output_file['filename'],
                    'ro_url': ro_filename,
                    'en_url': en_filename
                })
                print(f"  - SPECIAL: Termen special detectat! Se păstrează link-ul în EN.")

            # Actualizăm conținutul fișierului RO - întotdeauna înlocuim link-ul EN
            ro_updated_content, ro_modified = update_flags_section(ro_file['content'], None, en_link_in_output, is_special)

            # Actualizăm conținutul fișierului OUTPUT - întotdeauna înlocuim link-ul RO
            output_updated_content, output_modified = update_flags_section(output_file['content'], ro_link_in_ro, None, is_special)

            # Verificăm dacă s-au făcut modificări
            if not ro_modified and not output_modified:
                print(f"  - IGNORAT: Nu au fost necesare modificări.")
                continue

            # Salvăm fișierele actualizate
            with open(ro_file['path'], 'w', encoding='utf-8') as f:
                f.write(ro_updated_content)

            with open(output_file['path'], 'w', encoding='utf-8') as f:
                f.write(output_updated_content)

            print(f"  - SUCCES: Fișierele au fost actualizate.")
            processed_pairs += 1

    return processed_pairs, failed_pairs, special_terms

def main():
    # Definim directoarele
    ro_dir = r'e:\Carte\BB\17 - Site Leadership\Principal\ro'
    output_dir = r'e:\Carte\BB\17 - Site Leadership\alte\Ionel Balauta\Aryeht\Task 1 - Traduce tot site-ul\Doar Google Web\Andreea\Meditatii\2023\Iulia Python\output'

    # Verificăm dacă directoarele există
    if not os.path.exists(ro_dir):
        print(f"Directorul RO nu există: {ro_dir}")
        return

    if not os.path.exists(output_dir):
        print(f"Directorul OUTPUT nu există: {output_dir}")
        return

    # Procesăm fișierele
    print("Începere procesare fișiere...")
    processed_pairs, failed_pairs, special_terms = process_files(ro_dir, output_dir)

    # Afișăm rezultatul
    print(f"\nRezultat final:")
    print(f"- Perechi de fișiere actualizate cu succes: {processed_pairs}")
    print(f"- Perechi de fișiere cu erori: {failed_pairs}")

    # Afișăm termenii speciali
    if special_terms:
        print(f"\nTermeni speciali detectați ({len(special_terms)}):")
        print("-" * 80)
        for term in special_terms:
            print(f"ID: {term['id']}")
            print(f"RO: {term['ro_file']} -> URL: {term['ro_url']}")
            print(f"EN: {term['en_file']} -> URL: {term['en_url']}")
            print("-" * 80)

    print("\nProcesare completă!")

if __name__ == "__main__":
    main()