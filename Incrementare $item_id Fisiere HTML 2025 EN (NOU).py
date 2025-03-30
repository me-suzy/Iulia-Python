import os
import re
from collections import defaultdict

# Configuration
folders_to_scan = [
    r'e:\Carte\BB\17 - Site Leadership\Principal\en',
    r'e:\Carte\BB\17 - Site Leadership\Principal\en\FISIERE PYTHON HTML'
]
tracking_dir = r'e:\Carte\BB\17 - Site Leadership\Principal\en'
START_ID = 5000  # Changed from 1 to 5000
MAX_ID = 10000   # Changed from 5000 to 10000

def safe_print(text):
    """Handle special characters when printing"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('utf-8'))

def find_and_update_tracking_file(directory, new_id):
    """Update or create the tracking file"""
    try:
        pattern = re.compile(r'4-+am ajuns la \d+$')
        tracking_file = None

        for filename in os.listdir(directory):
            if pattern.search(filename):
                tracking_file = os.path.join(directory, filename)
                break

        if tracking_file:
            old_name = os.path.basename(tracking_file)
            new_name = re.sub(r'\d+$', str(new_id), old_name)
            os.rename(tracking_file, os.path.join(directory, new_name))
            safe_print(f"Fișierul de tracking actualizat: {old_name} -> {new_name}")
        else:
            new_name = f"4---------------------------am ajuns la {new_id}"
            with open(os.path.join(directory, new_name), 'w') as f:
                f.write(f"Ultimul ID folosit: {new_id}")
            safe_print(f"Fișier de tracking creat: {new_name}")

    except Exception as e:
        safe_print(f"Eroare la actualizarea fișierului de tracking: {str(e)}")

def process_files():
    # Data structures
    all_files = []
    filename_counts = defaultdict(list)
    duplicate_names = defaultdict(list)
    id_to_files = defaultdict(list)
    files_without_id = []
    duplicate_ids = defaultdict(list)
    out_of_range_ids = []

    # First pass: Find all HTML files
    safe_print("\n=== SCANARE FIȘIERE ===")
    for folder in folders_to_scan:
        safe_print(f"\nScanare folder: {os.path.basename(folder)}")
        for filename in os.listdir(folder):
            if filename.lower().endswith('.html'):
                full_path = os.path.join(folder, filename)
                all_files.append(full_path)
                filename_counts[filename].append(full_path)
                safe_print(f" - Găsit: {filename}")

    # Check for duplicate filenames
    for name, paths in filename_counts.items():
        if len(paths) > 1:
            duplicate_names[name] = paths

    # Second pass: Analyze IDs
    safe_print("\n=== ANALIZĂ ID-URI ===")
    id_pattern = re.compile(r'<!-- \s*\$item_id\s*=\s*(\d+);.*?-->')

    safe_print("Se analizează următoarele fișiere:")
    for file_path in all_files:
        filename = os.path.basename(file_path)
        safe_print(f" - Analiză ID pentru: {filename}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()

        matches = id_pattern.findall(content)
        if not matches:
            files_without_id.append(filename)
            safe_print("   ! Fișierul nu conține ID")
            continue

        file_id = int(matches[0])
        id_to_files[file_id].append(filename)
        safe_print(f"   ID găsit: {file_id}")

        if file_id > MAX_ID:
            out_of_range_ids.append((filename, file_id))
            safe_print(f"   ! ATENȚIE: ID depășește limita maximă ({MAX_ID})")

        # Check if this ID is duplicate (we'll know after full scan)
        if len(id_to_files[file_id]) > 1:
            safe_print(f"   ! ATENȚIE: ID duplicat (mai apare în: {id_to_files[file_id][0]})")

    # Find duplicate IDs
    for file_id, files in id_to_files.items():
        if len(files) > 1:
            duplicate_ids[file_id] = files

    # Generate the exact report format requested
    safe_print("\n" + "="*50)
    safe_print("REZULTATE ANALIZĂ:")
    safe_print("="*50)
    safe_print(f"Total fișiere HTML găsite: {len(all_files)}")
    safe_print(f"Fișiere fără ID: {len(files_without_id)}")
    safe_print(f"Fișiere cu ID-uri peste limită ({MAX_ID}): {len(out_of_range_ids)}")
    safe_print(f"ID-uri duplicate: {len(duplicate_ids)}")
    safe_print("="*50)

    # Files without ID
    if files_without_id:
        safe_print("\nFIȘIERE FĂRĂ ID:")
        for i, filename in enumerate(sorted(files_without_id), 1):
            safe_print(f"{i}. {filename}")

    # Duplicate IDs
    if duplicate_ids:
        safe_print("\nID-URI DUPLICATE:")
        for i, (file_id, files) in enumerate(sorted(duplicate_ids.items()), 1):
            safe_print(f"{i}. ID {file_id} este folosit în {len(files)} fișiere:")
            for j, filename in enumerate(sorted(files), 1):
                safe_print(f"   {j}. {filename}")

    # Duplicate filenames
    if duplicate_names:
        safe_print("\nS-au detectat urmatoarele fisiere cu acelasi nume:")
        for name, paths in duplicate_names.items():
            safe_print(f"\nNume duplicat: {name}")
            for path in paths:
                safe_print(f" - {path}")

    # Determine if we need to reset IDs
    needs_reset = bool(files_without_id or out_of_range_ids or duplicate_ids)

    if needs_reset:
        safe_print("\nS-au detectat probleme cu ID-urile care necesită resetare.")

    # Process files to reassign IDs sequentially starting from START_ID
    safe_print("\n=== REATRIBUIRE ID-URI ===")
    current_id = START_ID  # Start from 5000 instead of 1
    all_files_sorted = sorted(all_files, key=lambda x: os.path.basename(x).lower())
    files_processed = 0

    for file_path in all_files_sorted:
        filename = os.path.basename(file_path)
        safe_print(f"Procesez: {filename}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()

        # Get existing ID for reporting
        existing_id = None
        matches = id_pattern.findall(content)
        if matches:
            existing_id = int(matches[0])

        # Check if we've reached the maximum ID
        if current_id > MAX_ID:
            safe_print("   ! ATENȚIE: Limita maximă de ID-uri atinsă!")
            break

        # Replace with new sequential ID
        new_content = re.sub(
            r'<!-- \s*\$item_id\s*=\s*\d+;.*?-->',
            f'<!-- $item_id = {current_id}; // Replace that with your rating id -->',
            content
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if existing_id and existing_id != current_id:
            safe_print(f"  ID modificat: {existing_id} -> {current_id}")
        else:
            safe_print(f"  ID atribuit: {current_id}")

        current_id += 1
        files_processed += 1

    # Update tracking file with the new maximum ID
    new_max_id = current_id - 1
    find_and_update_tracking_file(tracking_dir, new_max_id)

    safe_print("\n" + "="*50)
    safe_print("REZUMAT FINAL:")
    safe_print("="*50)
    safe_print(f"Total fișiere procesate: {files_processed}")
    safe_print(f"Primul ID atribuit: {START_ID}")
    safe_print(f"Ultimul ID atribuit: {new_max_id}")
    if files_processed < len(all_files):
        safe_print(f"Fișiere neprocesate: {len(all_files) - files_processed} (limita de {MAX_ID} ID-uri a fost atinsă)")
    safe_print("="*50)

if __name__ == "__main__":
    process_files()