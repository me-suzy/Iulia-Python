import os
import re
import unidecode
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from datetime import datetime

def make_links_clickable(text):
    # Identifică și transformă linkurile în format <a href="...">...</a>
    return re.sub(r'(https?://[^\s]+)', r'<a href="\1">\1</a>', text)

def add_content_to_meta(html_content, content_to_add):
    meta_pattern = r'<meta name="description" content="(.*?)">'
    match = re.search(meta_pattern, html_content)
    if match:
        old_meta_tag = match.group(0)
        new_content = re.sub(r'"', '', content_to_add)
        new_meta_tag = f'<meta name="description" content="{new_content}">'
        updated_html_content = html_content.replace(old_meta_tag, new_meta_tag)
        return updated_html_content
    else:
        return html_content

def extract_data_from_docx(file_path):
    doc = Document(file_path)
    articles = []
    current_title = None
    current_body = []
    current_id = None
    is_id_line = False

    for para in doc.paragraphs:
        text = para.text.strip()

        # Verifică dacă paragraful este un titlu (centrat și nu este ID)
        if para.alignment == WD_PARAGRAPH_ALIGNMENT.CENTER and text and not text.startswith("ID:"):
            # Dacă avem deja un titlu, salvăm articolul anterior
            if current_title:
                articles.append((current_title, current_body, current_id))
                current_body = []
                current_id = None
            current_title = text
            is_id_line = True  # Următorul paragraf ar putea fi ID-ul
        # Verifică dacă paragraful este linia de ID
        elif is_id_line and text.startswith("ID:"):
            current_id = text.replace("ID:", "").strip()
            is_id_line = False
        # Altfel, este conținut de paragraf
        elif current_title and text:
            is_id_line = False  # Resetăm flag-ul
            formatted_text = []
            for run in para.runs:
                # Verificăm dacă textul este bold, italic, sau ambele
                if run.bold and run.italic:
                    formatted_text.append(f'<strong><em>{run.text}</em></strong>')
                elif run.bold:
                    formatted_text.append(f'<strong>{run.text}</strong>')
                elif run.italic:
                    formatted_text.append(f'<em>{run.text}</em>')
                else:
                    formatted_text.append(run.text)
            paragraph_text = ''.join(formatted_text)
            paragraph_text = make_links_clickable(paragraph_text)  # Adaugă linkuri clickable
            current_body.append(paragraph_text)

    # Adăugăm ultimul articol
    if current_title:
        articles.append((current_title, current_body, current_id))

    return articles

def remove_diacritics(text):
    return unidecode.unidecode(text)

def generate_filename(title):
    normalized_title = remove_diacritics(title.lower())
    normalized_title = re.sub(r'[^a-z0-9\-]+', '-', normalized_title)
    normalized_title = re.sub(r'-+', '-', normalized_title).strip('-')
    return f"{normalized_title}.html"

def format_body(body):
    formatted_body = ""
    for paragraph in body:
        paragraph = paragraph.strip()

        # Detectăm dacă paragraful începe cu numerotare (ex. "1. ", "2. " etc.)
        numbered_paragraph = re.match(r'^(\d+\.\s+)(.*)', paragraph)
        if numbered_paragraph:
            # Extragem numărul și restul paragrafului
            num = numbered_paragraph.group(1)
            rest_of_paragraph = numbered_paragraph.group(2)

            # Aplicăm stilizare: numărul va fi bold și restul textului va rămâne normal
            formatted_body += f'<p class="text_obisnuit"><span class="text_obisnuit2"><strong>{num}</strong></span>{rest_of_paragraph}</p>\n'
        else:
            # Dacă nu există numerotare, procesăm paragraful normal
            formatted_body += f'<p class="text_obisnuit">{paragraph}</p>\n'

    return formatted_body

def capitalize_title(title):
    # Split the title into words and capitalize each word
    words = title.split()
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)

def update_html_content(html_content, title, first_sentence, body, filename, article_id):
    # Adăugăm ID-ul articolului la începutul fișierului
    if article_id:
        id_comment = f'<!-- $item_id = {article_id}; // ID-ul din fisierul limba romana -->\n'
        # Verificăm dacă există deja un comentariu de ID
        if '<!-- $item_id =' not in html_content:
            # Adăugăm comentariul la începutul fișierului
            html_content = id_comment + html_content
        else:
            # Înlocuim comentariul existent
            html_content = re.sub(r'<!-- \$item_id = \d+;.*?-->\n?', id_comment, html_content)

    title_without_diacritics = remove_diacritics(title)
    capitalized_title = capitalize_title(title_without_diacritics)

    html_content = re.sub(r'<title>.*?</title>', f'<title>{title_without_diacritics} | Neculai Fantanaru (en)</title>', html_content)
    html_content = re.sub(r'<h1 class="den_articol" itemprop="name">.*?</h1>', f'<h1 class="den_articol" itemprop="name">{title}</h1>', html_content)

    html_content = html_content.replace('zzz.html', filename)

    # Extragem textul bold doar din acest articol
    bold_text = extract_bold_from_body(body)

    meta_desc = f'<meta name="description" content="{bold_text}">'
    html_content = re.sub(r'<meta name="description" content=".*?">', meta_desc, html_content)

    formatted_body = format_body(body)
    html_content = re.sub(r'<!-- SASA-1 -->.*?<!-- SASA-2 -->', f'<!-- SASA-1 -->\n{formatted_body}\n<!-- SASA-2 -->', html_content, flags=re.DOTALL)

    current_date = datetime.now().strftime("%B %d, %Y")
    html_content = re.sub(r'On .*?, in', f'On {current_date}, in', html_content)

    html_content = re.sub(r'<title>.*?</title>', f'<title>{capitalized_title} | Neculai Fantanaru (en)</title>', html_content)
    html_content = re.sub(r'<h1 class="den_articol" itemprop="name">.*?</h1>', f'<h1 class="den_articol" itemprop="name">{capitalize_title(title)}</h1>', html_content)

    return html_content

def extract_bold_from_body(body_paragraphs):
    """Extrage textul bold din paragrafele corpului articolului curent."""
    bold_text_parts = []

    for paragraph in body_paragraphs:
        # Caută toate secțiunile bold din text
        bold_matches = re.findall(r'<strong>(.*?)</strong>', paragraph)
        bold_text_parts.extend(bold_matches)

    # Concatenăm toate părțile bold găsite
    bold_text = ' '.join(bold_text_parts).strip()

    # Curățăm textul de tag-uri HTML care ar putea fi rămase
    bold_text = re.sub(r'<[^>]*>', '', bold_text)

    # Curățăm textul - eliminare ghilimele și alte caractere problematice
    bold_text = re.sub(r'["*<>]', '', bold_text)

    # Eliminăm spațiile multiple
    bold_text = re.sub(r'\s+', ' ', bold_text)

    return bold_text

def post_process_html(html_content):
    # Înlocuire string "NBSP" cu spațiu
    html_content = html_content.replace("NBSP", " ")

    # Înlocuire caracter non-breaking space (U+00A0) cu spațiu normal
    html_content = html_content.replace("\u00A0", " ")

    # Înlocuire entitate HTML &nbsp; cu spațiu normal
    html_content = html_content.replace("&nbsp;", " ")

    return html_content

def extract_text_obisnuit2(html_content):
    pattern = r'<p class="text_obisnuit2">(.*?)</p>'
    matches = re.findall(pattern, html_content, re.DOTALL)
    cleaned_text = ' '.join(matches).replace('"', '')
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)

    # Limităm la primele 8 propoziții și eliminăm orice text care nu ar trebui să fie în meta description
    description = ' '.join(sentences[:8]).strip()

    # Eliminăm textul nedorit
    if "Latest articles accessed by readers" in description:
        description = description.split("Latest articles accessed by readers")[0].strip()

    return description

def clean_meta_description(description):
    # Remove quotation marks, asterisks, and colons
    cleaned = re.sub(r'["*]', '', description)

    # Remove HTML tags, including partial tags like <e
    cleaned = re.sub(r'<[^>]*>', '', cleaned)

    # Remove any remaining <e characters
    cleaned = re.sub(r'<e ', ' ', cleaned)

    # Remove any remaining < or > characters
    cleaned = re.sub(r'[<>]', '', cleaned)

    # Replace multiple spaces with a single space
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Trim leading and trailing whitespace
    cleaned = cleaned.strip()

    return cleaned

# The update_meta_description function remains the same
def update_meta_description(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    text_obisnuit2 = extract_text_obisnuit2(content)

    if text_obisnuit2:
        cleaned_description = clean_meta_description(text_obisnuit2)

        updated_content = re.sub(
            r'<meta name="description" content=".*?">',
            f'<meta name="description" content="{cleaned_description}">',
            content
        )

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)

def remove_empty_paragraphs(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Găsim secțiunea dintre ARTICOL START și ARTICOL FINAL
    pattern = r'(<!-- ARTICOL START -->.*?<!-- ARTICOL FINAL -->)'
    article_section = re.search(pattern, content, re.DOTALL)

    if article_section:
        article_content = article_section.group(1)
        # Eliminăm paragrafele goale
        updated_article_content = re.sub(r'<p class="text_obisnuit"></p>\s*', '', article_content)
        # Înlocuim secțiunea originală cu cea actualizată
        content = content.replace(article_content, updated_article_content)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def format_numbered_paragraphs(content):
    # Înlocuiește paragrafele care încep cu un număr urmat de punct
    content = re.sub(
        r'<strong>(\d+\.\s+)</strong>(.*?)</p>',
        r'<p class="text_obisnuit"><span class="text_obisnuit2">\1</span>\2</p>',
        content
    )
    return content

def final_regex_replacements(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    content = format_numbered_paragraphs(content)

    # Înlocuire pentru paragrafele cu <p class="text_obisnuit"><strong><em>...</em></strong>
    # Devine: <p class="text_obisnuit2"><em>...</em></p>
    content = re.sub(
        r'<p class="text_obisnuit"><strong><em>(.*?)</em></strong></p>',
        r'<p class="text_obisnuit2"><em>\1</em></p>',
        content
    )

    # Devine: <p class="text_obisnuit2"><em>...</em></p>
    content = re.sub(
        r'<p class="text_obisnuit"><strong>(.*?)</strong></p>',
        r'<p class="text_obisnuit2">\1</p>',
        content
    )

    # Înlocuire pentru paragrafele cu <p class="text_obisnuit"><strong>...</strong> care conțin text după </strong>
    # Devine: <p class="text_obisnuit"><span class="text_obisnuit2">...</span> textul rămas</p>
    content = re.sub(
        r'<p class="text_obisnuit"><strong>(.*?)</strong>(.*?)</p>',
        r'<p class="text_obisnuit"><span class="text_obisnuit2">\1</span>\2</p>',
        content
    )

    # Înlocuire pentru adăugarea lui <br><br> înainte de paragrafele care conțin "* Notă:" în structura nouă
    content = re.sub(
        r'(<p class="text_obisnuit"><span class="text_obisnuit2">\* Note:)',
        r'<br><br>\n\1',
        content
    )

    # Alte înlocuiri specifice pentru curățarea tagurilor nedorite
    content = re.sub(r'<e</p>', '</p>', content)
    content = re.sub(r'</span></p>', '</p>', content)
    content = re.sub(r'<em></em>', '', content)
    content = re.sub(r'</strong>\s*<strong>', '', content)
    content = re.sub(r'<strong>', '', content)
    content = re.sub(r'</strong>', '', content)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def main():
    docx_path = "bebe.docx"
    html_path = "index.html"
    output_dir = "output"

    if not os.path.exists(docx_path):
        print(f"Error: File '{docx_path}' not found.")
        return

    if not os.path.exists(html_path):
        print(f"Error: File '{html_path}' not found.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    articles = extract_data_from_docx(docx_path)

    if not articles:
        print("No articles found in the document.")
        return

    for title, body, article_id in articles:
        filename = generate_filename(title)
        print(f"Processing article: {title}")
        print(f"Article ID: {article_id}")
        print(f"Generated filename: {filename}")

        with open(html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        if not body:
            print(f"Warning: Empty body for article '{title}'. Skipping.")
            continue

        updated_html = update_html_content(html_content, title, body[0], body, filename, article_id)

        # Aplicăm post-procesarea chiar înainte de salvare
        updated_html = post_process_html(updated_html)

        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(updated_html)

        # Actualizăm meta description-ul
        update_meta_description(output_path)

        # Eliminăm paragrafele goale
        remove_empty_paragraphs(output_path)

        # Aplicăm înlocuirile finale cu regex
        final_regex_replacements(output_path)

        print(f"Saved and updated meta description for: {filename}")

    print("All articles have been processed successfully.")

if __name__ == "__main__":
    main()