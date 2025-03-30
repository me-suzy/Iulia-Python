import os
import re

# Lista folderelor de scanat
folders_to_scan = [
    r'e:\Carte\BB\17 - Site Leadership\Principal\en',
    r'e:\Carte\BB\17 - Site Leadership\Principal\en\FISIERE PYTHON HTML'
]

# ID-ul de început
current_id = 5000

# Construim o listă cu toate fișierele HTML din cele două foldere
all_html_files = []
for folder_path in folders_to_scan:
    for html_file in os.listdir(folder_path):
        if html_file.endswith('.html'):
            all_html_files.append(os.path.join(folder_path, html_file))

# Sortăm fișierele alfabetic după numele de bază
all_html_files.sort(key=lambda x: os.path.basename(x).lower())

# Procesăm fiecare fișier și actualizăm ID-urile
for html_file_path in all_html_files:
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except UnicodeDecodeError:
        print(f"Eroare la decodare pentru {html_file_path}. Se încearcă cu encoding latin-1.")
        with open(html_file_path, 'r', encoding='latin-1') as file:
            html_content = file.read()

    # Înlocuim ID-ul vechi cu noul ID
    new_content, num_replaced = re.subn(
        r'<!-- \s*\$item_id\s*=\s*\d+;.*?-->',
        f'<!-- $item_id = {current_id}; // Replace that with your rating id -->',
        html_content
    )

    # Verificăm dacă s-a făcut înlocuirea
    if num_replaced > 0:
        with open(html_file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"ID-ul fișierului {os.path.basename(html_file_path)} a fost actualizat la {current_id}.")
        current_id += 1
    else:
        print(f"Nu s-a găsit un ID în fișierul {os.path.basename(html_file_path)}.")

print(f"\nUltimul ID folosit: {current_id - 1}")
print("Toate fișierele au fost procesate.")