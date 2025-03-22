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

def update_flags_section(file_content, ro_link, en_link):
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

    # Actualizăm link-ul EN, dacă este furnizat
    if en_link:
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

            # Actualizăm conținutul fișierului RO
            ro_updated_content, ro_modified = update_flags_section(ro_file['content'], None, en_link_in_output)

            # Actualizăm conținutul fișierului OUTPUT
            output_updated_content, output_modified = update_flags_section(output_file['content'], ro_link_in_ro, None)

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

    return processed_pairs, failed_pairs

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
    processed_pairs, failed_pairs = process_files(ro_dir, output_dir)

    print(f"\nRezultat final:")
    print(f"- Perechi de fișiere actualizate cu succes: {processed_pairs}")
    print(f"- Perechi de fișiere cu erori: {failed_pairs}")
    print("\nProcesare completă!")

if __name__ == "__main__":
    main()