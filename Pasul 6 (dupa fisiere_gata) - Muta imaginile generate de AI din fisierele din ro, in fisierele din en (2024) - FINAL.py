import os
import re

ro_directory = r'e:\Carte\BB\17 - Site Leadership\Principal 2022\ro'
en_directory = r'c:\Folder1\fisiere_gata'

def get_ro_filename(en_content):
   match = re.search(r'<li><a cunt_code="\+40" href="https://neculaifantanaru\.com/(.*?)\.html"', en_content)
   return match.group(1) if match else None

def get_image_url(content):
   img_match = re.search(r'<img src="(https://neculaifantanaru\.com/images/.*?_image\.jpg)"', content)
   return img_match.group(1) if img_match else None

def process_files():
   print("Start procesare fișiere...")

   for en_file in os.listdir(en_directory):
       if not en_file.endswith('.html'):
           continue

       print(f"\nProcesare: {en_file}")
       en_file_path = os.path.join(en_directory, en_file)

       try:
           with open(en_file_path, 'r', encoding='utf-8') as f:
               en_content = f.read()

           ro_filename = get_ro_filename(en_content)
           if not ro_filename:
               print(f"Nu s-a găsit link-ul RO în {en_file}")
               continue

           ro_file_path = os.path.join(ro_directory, f"{ro_filename}.html")
           if not os.path.exists(ro_file_path):
               print(f"Fișierul RO nu există: {ro_file_path}")
               continue

           print(f"Fișier RO găsit: {ro_filename}.html")

           with open(ro_file_path, 'r', encoding='utf-8') as f:
               ro_content = f.read()

           image_url = get_image_url(ro_content)
           if not image_url:
               print(f"Nu s-a găsit URL-ul imaginii în {ro_filename}.html")
               continue

           print(f"URL imagine găsit: {image_url}")

           # Înlocuiește imaginea în fișierul EN
           new_en_content = re.sub(
               r'<img src="https://neculaifantanaru\.com/images/.*?_image\.jpg"',
               f'<img src="{image_url}"',
               en_content
           )

           with open(en_file_path, 'w', encoding='utf-8') as f:
               f.write(new_en_content)

           print(f"Imagine actualizată în {en_file}")

       except Exception as e:
           print(f"Eroare la procesarea {en_file}: {str(e)}")

   print("\nProcesare terminată")

if __name__ == "__main__":
   process_files()