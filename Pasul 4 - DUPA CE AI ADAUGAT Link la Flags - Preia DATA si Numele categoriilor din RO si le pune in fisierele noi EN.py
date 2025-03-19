
# Fisierul are deja link-ul corespondent din RO, din sectiunea FLAGS

# Extrage informațiile de categorie din fișierul românesc:

# Data (tradusă din română în engleză, ex: "Octombrie" → "October")
# Link-ul categoriei (tradus folosind maparea, ex: "leadership-de-durata" → "leadership-that-lasts")
# Titlul categoriei (tradus folosind aceeași mapare)



import os
import re
from pathlib import Path

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

def translate_category_link(link, title):
    special_cases = {
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

    if link in special_cases:
        return special_cases[link]['link'], special_cases[link]['title']
    return link, title

def extract_romanian_link(content):
    pattern = r'<a href="https://neculaifantanaru\.com/(.*?)\.html"><img src="index_files/flag_lang_ro\.jpg"'
    match = re.search(pattern, content)
    return match.group(1) if match else None

def check_if_link_exists(content, basename):
    # Elimină extensia .html
    article_name = basename.replace('.html', '')
    # Verifică doar dacă numele articolului există în conținut, nu și calea exactă
    pattern = f'"{article_name}"'
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
            with open(ro_file, 'r', encoding='latin1') as f:
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

def update_en_file(en_file, category_info):
    with open(en_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if check_if_link_exists(content, os.path.basename(en_file)):
        print(f"Există deja datele din fișierul {en_file}")
        return False

    new_text = f'<td class="text_dreapta">On {category_info["date"]}, in <a href="https://neculaifantanaru.com/en/{category_info["category_link"]}.html" title="View all articles from {category_info["category_title"]}" class="external" rel="category tag">{category_info["category_title"]}</a>, by Neculai Fantanaru</td>'

    pattern = r'<td class="text_dreapta">On.*?class="external" rel="category tag">.*?</a>, by Neculai Fantanaru</td>'

    new_content = re.sub(pattern, new_text, content)

    with open(en_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True

def process_files():
    input_dir = r"e:\Carte\BB\17 - Site Leadership\alte\Ionel Balauta\Aryeht\Task 1 - Traduce tot site-ul\Doar Google Web\Andreea\Meditatii\2023\Iulia Python\output"
    ro_dir = r"e:\Carte\BB\17 - Site Leadership\Principal\ro"

    print("Start procesare fișiere...")

    for en_file in Path(input_dir).glob('*.html'):
        print(f"\nProcesare: {en_file.name}")

        try:
            with open(en_file, 'r', encoding='utf-8') as f:
                content = f.read()

            ro_link = extract_romanian_link(content)
            if ro_link:
                print(f"Link românesc găsit: {ro_link}")
                ro_file = Path(ro_dir) / f"{ro_link}.html"

                if ro_file.exists():
                    print(f"Procesare fișier românesc: {ro_file}")
                    category_info = extract_category_info(ro_file)
                    if category_info:
                        print(f"Info categorie găsit: {category_info}")
                        if update_en_file(en_file, category_info):
                            print(f"Fișier actualizat: {en_file.name}")
                    else:
                        print(f"Nu s-au găsit informații despre categorie în {ro_file}")
                else:
                    print(f"Fișierul românesc nu există: {ro_file}")
            else:
                print(f"Nu s-a găsit link românesc în {en_file.name}")
        except Exception as e:
            print(f"Eroare la procesarea {en_file}: {e}")

    print("\nProcesare terminată.")

if __name__ == "__main__":
    process_files()