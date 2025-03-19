import os
import re
from pathlib import Path
import unidecode

def translate_month(date_str):
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

    for ro, en in ro_to_en.items():
        if ro in date_str:
            return date_str.replace(ro, en)
    return date_str

def calculate_similarity(text1, text2):
    """
    Calculează un scor simplu de asemănare între două texte.
    Valori între 0 (complet diferite) și 1 (identice).
    """
    if not text1 or not text2:
        return 0

    # Normalizăm textele pentru comparație
    text1 = text1.lower()
    text2 = text2.lower()

    # Eliminăm diacriticele pentru o comparație mai bună
    text1 = unidecode.unidecode(text1)
    text2 = unidecode.unidecode(text2)

    # Calculăm similitudinea folosind un algoritm simplu
    words1 = set(re.findall(r'\b\w+\b', text1))
    words2 = set(re.findall(r'\b\w+\b', text2))

    if not words1 or not words2:
        return 0

    common_words = words1.intersection(words2)
    return len(common_words) / max(len(words1), len(words2))

def get_category_mapping():
    """
    Returnează o mapare bidirecțională între categoriile românești și englezești
    """
    # Mapare bidirecțională pentru link-uri și titluri
    category_map = {
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
        }
    }

    # Construim și maparea inversă (EN->RO)
    inverse_map = {}
    for ro_key, values in category_map.items():
        en_link = values['link']
        inverse_map[en_link] = {
            'link': ro_key,
            'title': ro_key.replace('-', ' ').title()  # O aproximare simplă
        }

    return category_map, inverse_map

def translate_category_link(link, title):
    category_map, _ = get_category_mapping()
    if link in category_map:
        return category_map[link]['link'], category_map[link]['title']
    return link, title

def get_filename_mappings():
    """
    Returnează o mapare directă între numele de fișiere românești și englezești
    """
    # Mapări directe cunoscute între nume de fișiere
    filename_map = {
        # RO -> EN
        "paradoxul-empatiei-pierdute": "the-paradox-of-lost-empathy",
        "intelepciunea": "wisdom",
        "calitatile-unui-lider": "qualities-of-a-leader",
        "ancestrum": "ancestor",
        # Adaugă mai multe mapări după necesitate
    }

    # Construim și maparea inversă (EN->RO)
    inverse_map = {en: ro for ro, en in filename_map.items()}

    return filename_map, inverse_map

def extract_romanian_link(content):
    pattern = r'<a href="https://neculaifantanaru\.com/(.*?)\.html"><img src="index_files/flag_lang_ro\.jpg"'
    match = re.search(pattern, content)
    return match.group(1) if match else None

def extract_english_link(content):
    pattern = r'<a href="https://neculaifantanaru\.com/en/(.*?)\.html"><img src="index_files/flag_lang_en\.jpg"'
    match = re.search(pattern, content)
    return match.group(1) if match else None

def extract_quote(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        quote_pattern = r'<p class="text_obisnuit2">(.*?)</p>'
        match = re.search(quote_pattern, content)
        return match.group(1).strip() if match else ''
    except Exception as e:
        print(f"Eroare la extragerea citatului din {file_path}: {e}")
        return ''

def extract_title(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        title_pattern = r'<h1 class="den_articol" itemprop="name">(.*?)</h1>'
        match = re.search(title_pattern, content)
        return match.group(1) if match else ''
    except Exception as e:
        print(f"Eroare la extragerea titlului din {file_path}: {e}")
        return ''

def check_if_link_exists(content, filename):
    pattern = f'href="https://neculaifantanaru.com/en/{filename}"'
    return bool(re.search(pattern, content))

def extract_category_info(ro_file):
    try:
        with open(ro_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        pattern = r'<td class="text_dreapta">On (.*?), in <a href="https://neculaifantanaru\.com/(.*?)\.html" title="Vezi toate articolele din (.*?)" class="external"'
        match = re.search(pattern, content)
        if match:
            link = match.group(2)
            title = match.group(3)
            translated_link, translated_title = translate_category_link(link, title)
            return {
                'date': translate_month(match.group(1)),
                'category_link': translated_link,
                'category_title': translated_title
            }
    except Exception as e:
        print(f"Eroare la citirea fișierului {ro_file}: {e}")
        try:
            with open(ro_file, 'r', encoding='latin1', errors='ignore') as f:
                content = f.read()
            pattern = r'<td class="text_dreapta">On (.*?), in <a href="https://neculaifantanaru\.com/(.*?)\.html" title="Vezi toate articolele din (.*?)" class="external"'
            match = re.search(pattern, content)
            if match:
                link = match.group(2)
                title = match.group(3)
                translated_link, translated_title = translate_category_link(link, title)
                return {
                    'date': translate_month(match.group(1)),
                    'category_link': translated_link,
                    'category_title': translated_title
                }
        except Exception as e:
            print(f"Eroare și la încercarea cu latin1: {e}")
    return None

def update_category_file(category_file, article_data, quote):
    try:
        with open(category_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if check_if_link_exists(content, article_data['filename']):
            print(f"Există deja datele din fișierul {article_data['filename']}")
            return False

        article_section = f'''      <table width="660" border="0">
            <tr>
              <td><span class="den_articol"><a href="https://neculaifantanaru.com/en/{article_data['filename']}" class="linkMare">{article_data['title']}</a></span></td>
              </tr>
              <tr>
              <td class="text_dreapta">On {article_data['date']}, in <a href="https://neculaifantanaru.com/en/{article_data['category_link']}.html" title="View all articles from {article_data['category_title']}" class="external" rel="category tag">{article_data['category_title']}</a>, by Neculai Fantanaru</td>
            </tr>
          </table>
          <p class="text_obisnuit2">{quote}</p>
          <table width="552" border="0">
            <tr>
              <td width="552"><div align="right" id="external2"><a href="https://neculaifantanaru.com/en/{article_data['filename']}">read more </a><a href="https://neculaifantanaru.com/en/" title=""><img src="Arrow3_black_5x7.gif" alt="" width="5" height="7" class="arrow" /></a></div></td>
            </tr>
          </table>
          <p class="text_obisnuit"></p>'''

        start_marker = '<!-- ARTICOL CATEGORIE START -->'
        end_marker = '<!-- ARTICOL CATEGORIE FINAL -->'

        start_pos = content.find(start_marker)
        div_start = content.find('<div align="justify">', start_pos)
        end_pos = content.find(end_marker)

        if start_pos != -1 and end_pos != -1 and div_start != -1:
            is_2024 = "2024" in article_data['date']
            print(f"Am introdus articol din 2024: {is_2024}")

            if is_2024:
                print("Inserare la început...")
                div_end = div_start + len('<div align="justify">')
                new_content = (content[:div_end] + '\n' + article_section + content[div_end:])
            else:
                print("Inserare la sfârșit...")
                section_content = content[start_pos:end_pos]
                last_table_pos = section_content.rfind('</table')
                if last_table_pos != -1:
                    insert_position = start_pos + last_table_pos + len('</table>\n      <p class="text_obisnuit"></p>')
                    new_content = (content[:insert_position] + '\n' + article_section +
                                 f'''\n          </div>
          <p align="justify" class="text_obisnuit style3"> </p>''' + content[end_pos:])

            with open(category_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Eroare la actualizarea fișierului de categorie {category_file}: {e}")
        return False

def find_similar_title_in_dir(en_title, directory):
    """
    Caută în directorul specificat fișiere cu titluri similare.
    Returnează calea către cel mai similar fișier.
    """
    print(f"Căutare fișier cu titlu similar pentru: '{en_title}'")

    best_match = None
    best_score = 0

    for file_path in Path(directory).glob('*.html'):
        try:
            # Extragem titlul fișierului
            ro_title = extract_title(file_path)
            if not ro_title:
                continue

            # Calculăm similitudinea
            score = calculate_similarity(en_title, ro_title)

            # Afișăm informații pentru debugging
            if score > 0.3:
                print(f"Candidat: {file_path.name}, Titlu: '{ro_title}', Scor: {score:.2f}")

            # Actualizăm cea mai bună potrivire
            if score > best_score:
                best_score = score
                best_match = file_path
        except Exception as e:
            print(f"Eroare la procesarea {file_path}: {e}")
            continue

    # Returnăm cea mai bună potrivire dacă scorul este suficient de bun
    if best_match and best_score > 0.45:
        print(f"Cea mai bună potrivire: {best_match.name} (Scor: {best_score:.2f})")
        return str(best_match)
    else:
        print(f"Nu s-a găsit o potrivire suficient de bună (cel mai bun scor: {best_score:.2f})")
        return None

def find_real_ro_correspondent(en_file_path):
    """
    Găsește corespondentul românesc REAL pentru un fișier englezesc,
    chiar dacă secțiunea FLAGS din fișierul englezesc indică altceva.
    """
    ro_dir = r"e:\Carte\BB\17 - Site Leadership\Principal\ro"
    en_filename = Path(en_file_path).stem

    print(f"Căutare corespondent real pentru: {en_filename}")

    # Metoda 1: Verificăm mapările directe
    ro_to_en_map, en_to_ro_map = get_filename_mappings()
    if en_filename in en_to_ro_map:
        ro_filename = en_to_ro_map[en_filename]
        ro_path = os.path.join(ro_dir, f"{ro_filename}.html")
        if os.path.exists(ro_path):
            print(f"Corespondent găsit prin mapare directă: {ro_filename}")
            return ro_path

    # Metoda 2: Căutăm după similitudine de titlu
    en_title = extract_title(en_file_path)
    if en_title:
        similar_file = find_similar_title_in_dir(en_title, ro_dir)
        if similar_file:
            return similar_file

    # Metoda 3: Verificăm referințe încrucișate
    try:
        for ro_file in Path(ro_dir).glob('*.html'):
            try:
                with open(ro_file, 'r', encoding='utf-8', errors='ignore') as f:
                    ro_content = f.read()

                # Verificăm dacă fișierul românesc are referință către cel englezesc
                if f"en/{en_filename}.html" in ro_content:
                    print(f"Corespondent găsit prin referință în conținut: {ro_file.name}")
                    return str(ro_file)
            except Exception as e:
                print(f"Eroare la verificarea referințelor pentru {ro_file.name}: {e}")
                continue
    except Exception as e:
        print(f"Eroare la căutarea referințelor: {e}")

    # Verificare specială pentru "ancestor.html" -> "ancestrum.html"
    if en_filename == "ancestor":
        ro_path = os.path.join(ro_dir, "ancestrum.html")
        if os.path.exists(ro_path):
            print(f"Corespondent special găsit pentru ancestor: ancestrum.html")
            return ro_path

    # Dacă am ajuns aici, înseamnă că nu am găsit un corespondent real
    # Ca ultimă soluție, verificăm ce există în secțiunea FLAGS actuală
    try:
        with open(en_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            en_content = f.read()

        flags_section = re.search(r'<!-- FLAGS_1 -->.*?<!-- FLAGS -->', en_content, re.DOTALL)
        if flags_section:
            ro_link = extract_romanian_link(flags_section.group(0))
            if ro_link:
                ro_path = os.path.join(ro_dir, f"{ro_link}.html")
                if os.path.exists(ro_path):
                    print(f"Corespondent curent din FLAGS: {ro_link}")
                    return ro_path
    except Exception as e:
        print(f"Eroare la verificarea FLAGS curent: {e}")

    # Nu am găsit niciun corespondent
    print(f"Nu s-a găsit niciun corespondent real pentru {en_filename}")
    return None

def update_flags_section(en_file_path, ro_file_path):
    """
    Actualizează secțiunea FLAGS din fișierul englezesc pentru a reflecta
    corespondența corectă cu fișierul românesc.
    """
    try:
        # Obține numele fișierelor (fără extensie)
        en_filename = Path(en_file_path).stem
        ro_filename = Path(ro_file_path).stem

        print(f"Actualizare FLAGS: EN={en_filename}, RO={ro_filename}")

        # Verificăm ce există în FLAGS în prezent
        with open(en_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            en_content = f.read()

        current_ro_link = extract_romanian_link(en_content)
        print(f"Link românesc curent în FLAGS: {current_ro_link}")

        # Dacă link-ul curent este deja corect, nu facem nicio modificare
        if current_ro_link == ro_filename:
            print(f"Link-ul românesc este deja corect: {ro_filename}")
            return False

        # Căutăm secțiunea FLAGS
        flags_pattern = r'(<!-- FLAGS_1 -->.*?<!-- FLAGS -->)'
        flags_match = re.search(flags_pattern, en_content, re.DOTALL)

        if not flags_match:
            print(f"Nu s-a găsit secțiunea FLAGS în {en_file_path}")
            return False

        old_flags_section = flags_match.group(1)

        # Înlocuim link-ul către versiunea română
        new_flags_section = re.sub(
            r'<a href="https://neculaifantanaru\.com/([^"]+)\.html"><img src="index_files/flag_lang_ro\.jpg"',
            f'<a href="https://neculaifantanaru.com/{ro_filename}.html"><img src="index_files/flag_lang_ro.jpg"',
            old_flags_section
        )

        # Înlocuim și link-ul către versiunea engleză pentru a fi siguri
        new_flags_section = re.sub(
            r'<a href="https://neculaifantanaru\.com/en/([^"]+)\.html"><img src="index_files/flag_lang_en\.jpg"',
            f'<a href="https://neculaifantanaru.com/en/{en_filename}.html"><img src="index_files/flag_lang_en.jpg"',
            new_flags_section
        )

        # Verificăm dacă s-a făcut vreo modificare
        if new_flags_section == old_flags_section:
            print("Nu s-a făcut nicio modificare în FLAGS")
            return False

        # Aplicăm modificarea în fișier
        updated_content = en_content.replace(old_flags_section, new_flags_section)

        with open(en_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        print(f"FLAGS actualizat de la {current_ro_link} la {ro_filename}")
        return True

    except Exception as e:
        print(f"Eroare la actualizarea FLAGS: {e}")
        return False

def process_files():
    input_dir = r"e:\Carte\BB\17 - Site Leadership\alte\Ionel Balauta\Aryeht\Task 1 - Traduce tot site-ul\Doar Google Web\Andreea\Meditatii\2023\Iulia Python\output"
    ro_dir = r"e:\Carte\BB\17 - Site Leadership\Principal\ro"
    category_dir = r"e:\Carte\BB\17 - Site Leadership\Principal\en"

    print("=== Start procesare fișiere ===")

    files_processed = 0
    files_flags_updated = 0
    files_category_updated = 0
    files_skipped = 0
    files_with_errors = 0

    for en_file in Path(input_dir).glob('*.html'):
        print(f"\n=== Procesare: {en_file.name} ===")

        try:
            # Găsim CORESPONDENTUL REAL românesc, nu cel din FLAGS
            ro_file = find_real_ro_correspondent(en_file)

            if not ro_file:
                print(f"Nu s-a putut găsi corespondentul românesc real pentru {en_file.name}")
                files_skipped += 1
                continue

            # Afișăm informații despre corespondență
            print(f"Fișier românesc corespunzător REAL: {Path(ro_file).name}")

            # Actualizăm secțiunea FLAGS cu corespondentul REAL
            flags_updated = update_flags_section(en_file, ro_file)
            if flags_updated:
                files_flags_updated += 1
                print(f"FLAGS actualizat cu succes pentru: {en_file.name}")
            else:
                print(f"FLAGS nu a necesitat actualizare pentru: {en_file.name}")

            # Extragem informații necesare pentru categoria din fișierul românesc
            ro_file_path = Path(ro_file)
            category_info = extract_category_info(ro_file_path)

            if not category_info:
                print(f"Nu s-au putut extrage informații despre categorie din: {ro_file_path.name}")
                files_skipped += 1
                continue

            # Extragem quote și titlu din fișierul englezesc
            quote = extract_quote(en_file)
            title = extract_title(en_file)

            # Adăugăm informațiile la obiectul category_info
            category_info['filename'] = en_file.name
            category_info['title'] = title

            # Actualizăm fișierul de categorie
            category_file = Path(category_dir) / f"{category_info['category_link']}.html"
            print(f"Actualizare categorie: {category_file.name}")

            was_updated = update_category_file(category_file, category_info, quote)

            if was_updated:
                print(f"Fișier de categorie actualizat cu succes: {category_file.name}")
                files_category_updated += 1
            else:
                print(f"Fișierul de categorie nu a necesitat actualizare")
                files_skipped += 1

            files_processed += 1

        except Exception as e:
            print(f"Eroare la procesarea {en_file}: {e}")
            files_with_errors += 1

    # Afișăm statistici finale
    print("\n=== Rezumat procesare ===")
    print(f"Total fișiere procesate: {files_processed}")
    print(f"Fișiere cu FLAGS actualizate: {files_flags_updated}")
    print(f"Fișiere cu categorii actualizate: {files_category_updated}")
    print(f"Fișiere omise: {files_skipped}")
    print(f"Fișiere cu erori: {files_with_errors}")
    print("\n=== Procesare terminată ===")

if __name__ == "__main__":
    process_files()