import argparse
import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
import subprocess
from urllib.parse import urlparse
import signal
import sys
import ast 

# ======================= # 
# CONFIGURACIÓN PRINCIPAL # 
# ======================= #
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

DELAY_EPISODES = 1
DELAY_DOWNLOADS = 5

# control de salida del programa
def def_handler(sig, frame):
    print("\n\n[!] Saliendo...")
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

# manejo de la url
def get_base_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

# manejo del nombre del anime a través de su url
def get_anime_name(url):
    return url.rstrip("/").split("/")[-1]

# formato del título 
def format_anime_title(anime_name):
    """El nombre del archivo pasa de 'naruto-shippuden' a 'Naruto Shippuden'"""
    return anime_name.replace("-", " ").title()

# nombramiento a los archivos .mp4 descargados
def episode_filename(anime_title, ep_num):
    """Genera el nombre del archivo: 'Naruto - Episodio 1.mp4'"""
    return f"{anime_title} - Episodio {ep_num}.mp4"

# se crea una estructura de directorios por cada anime
def setup_dirs(anime_name):
    """
    Crea la estructura de directorios:
        Anime Title/
        └── links/
    """
    anime_title = format_anime_title(anime_name)
    anime_dir = anime_title
    links_dir = os.path.join(anime_dir, "links")

    os.makedirs(links_dir, exist_ok=True)

    print(f"[+] Directorio creado: {anime_dir}/")
    return anime_dir, links_dir, anime_title

# =================================== #
# EXTRACCIÓN DE LA LISTA DE EPISODIOS # 
# =======[desde el JavaScript]======= #
def get_episode_list(session, anime_url, base_url):
    print("[+] Obteniendo lista de episodios...")

    res = session.get(anime_url, headers=HEADERS)

    match = re.search(r'var episodes = (\[\[.*?\]\]);', res.text)

    if not match:
        print("[!] No se encontró la lista de episodios")
        return []

    episodes_data = ast.literal_eval(match.group(1))

    slug = anime_url.rstrip("/").split("/")[-1]

    episodes = [
        (ep[0], f"{base_url}/ver/{slug}-{ep[0]}")
        for ep in episodes_data
    ]

    episodes.sort(key=lambda x: x[0])

    print(f"[+] {len(episodes)} episodios encontrados")

    return episodes

# ============================= #
# EXTRAER LINKS (MULTISERVIDOR) # 
# ====[Mega, 1Fichier, etc]==== #
def extract_links(session, episode_url):
    try:
        res = session.get(episode_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        links = {}

        rows = soup.find_all("tr")

        for row in rows:
            cols = row.find_all("td")

            if len(cols) < 2:
                continue

            server = cols[0].text.strip()
            a_tag = row.find("a", href=True)
            
            if not a_tag:
                continue
           
            href = a_tag["href"]

            if server not in links:
                links[server] = []

            links[server].append(href)

        return links

    except Exception as e:
        print(f"[x] Error extrayendo links: {e}")
        return {}

# ================================ #
# GUARDAR LOS RESULTADOS OBTENIDOS #
# ======[ej: anime-mega.txt]====== #
def save_links(all_links, anime_name, links_dir, anime_title):
    print("\n[+] Guardando archivos de enlaces extraídos...")

    for server, entries in all_links.items():
        filename = os.path.join(links_dir, f"{anime_title} - {server}.txt")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Anime: {anime_title}\n")
            f.write(f"Servidor: {server}\n\n")

            for ep_num, link in entries:
                if link:
                    f.write(f"Episodio {ep_num}: {link}\n")
                else:
                    f.write(f"Episodio {ep_num}: ERROR\n")

        print(f"[+] {filename}")

# =============================== # 
# DESCARGAR DESDE UN ARCHIVO .TXT #
# ==========[solo MEGA]========== #
def download_from_file(file_path):
    print(f"[+] Leyendo archivo: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    except Exception:
        print(f"[x] No se pudo leer el archivo")
        return

    # leer los metadatos del encabezado
    anime_title = None
    for line in lines:
        if line.lower().startswith("anime:"):
            anime_title = line.split(":", 1)[1].strip()
            break

    if not anime_title:
        print(f"[x] No se encontró el nombre del anime en el archivo")
        return

    # directorio destino con el mismo nombre del anime
    anime_dir = anime_title
    os.makedirs(anime_dir, exist_ok=True)

    # parsear episodios
    entries = [] # lista de (ep_num, link)
    for line in lines:
        if "http" not in line:
            continue
        m = re.match(r'Episodio\s+(\d+):\s+(http\S+)', line.strip())
        if m:
            entries.append((int(m.group(1)), m.group(2)))

    print(f"[+] Enlaces encontrados: {len(entries)}\n")

    for ep_num, link in entries:
        dest = os.path.join(anime_dir, episode_filename(anime_title, ep_num))

        # omitir si el episodio ya existe
        if os.path.exists(dest):
            print(f"[=] Episodio {ep_num} ya descargado. Omitiendo...")
            continue

        print(f"[↓] Descargando episodio {ep_num}")

        try:
            subprocess.run([
                "megadl",
                "--path", dest, 
                link
            ], check=True)

            print(f"[✓] Episodio {ep_num} descargado")

        except subprocess.CalledProcessError:
            print(f"[x] Error con el episodio {ep_num}")

        time.sleep(DELAY_DOWNLOADS)

# ================= #
# SCRAPER PRINCIPAL #
# ================= #
def scraper(anime_url):
    session = requests.Session()

    base_url = get_base_url(anime_url)
    anime_name = get_anime_name(anime_url)

    anime_dir, links_dir, anime_title = setup_dirs(anime_name)
    
    episodes = get_episode_list(session, anime_url, base_url)
    
    all_links = {}

    print("\n[+] Procesando episodios...\n")

    for ep_num, ep_url in episodes:
        print(f"[+] Episodio {ep_num}")

        ep_links = extract_links(session, ep_url)

        for server, links in ep_links.items():
            if server not in all_links:
                all_links[server] = []

            link = links[0] if links else None
            all_links[server].append((ep_num, link))

        time.sleep(DELAY_EPISODES)

    save_links(all_links, anime_name, links_dir, anime_title)

# ================= #
# FUNCIÓN PRINCIPAL # 
# ================= #
def main():
    parser = argparse.ArgumentParser(description="AnimeFLV Tool")
    
    parser.add_argument("-u", "--url", help="URL del anime (modo scraping)")
    parser.add_argument("-f", "--file", help="Archivo .txt de enlaces (modo descarga)")

    args = parser.parse_args()

    if args.url and args.file:
        print("[!] No puedes usar -u y -f al mismo tiempo")
        return

    if not args.url and not args.file: 
        print(f"[!] Debes usar -u [URL] o -f [FILE]")
        return

    if args.url:
        scraper(args.url)

    elif args.file:
        download_from_file(args.file)

if __name__ == "__main__":
    main()
