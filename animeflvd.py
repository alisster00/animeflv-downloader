import argparse
import requests
from bs4 import BeautifulSoup
import json
import base64
import time
import re
import subprocess
from urllib.parse import urlparse
import signal
import sys
import ast 

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

DELAY_EPISODES = 2
DELAY_DOWNLOADS = 5

def def_handler(sig, frame):
    print("\n\n[!] Saliendo...")
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

def get_base_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def decode_cookie(cookie_value):
    try:
        cookie_value = cookie_value.replace('-', '+').replace('_', '/')
        padding = '=' * (-len(cookie_value) % 4)
        cookie_value += padding

        decoded = base64.b64decode(cookie_value).decode('utf-8')
        return json.loads(decoded)
    except:
        return None

def get_anime_name(url):
    return url.rstrip("/").split("/")[-1]

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

def get_mega_link(session, episode_url):
    try:
        res = session.get(episode_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        rows = soup.find_all("tr")

        for row in rows:
            cols = row.find_all("td")

            if len(cols) >= 1 and cols[0].text.strip() == "MEGA":
                a_tag = row.find("a", href=True)
                if a_tag:
                    return a_tag["href"]

        return None

    except Exception as e:
        print(f"[!] Error obteniendo links de MEGA: {e}")
        return None

def resolve_link(session, linkinpork_url):
    try:
        session.get(linkinpork_url, headers=HEADERS)

        cookie = session.cookies.get("_cf_uid")

        if not cookie:
            return None

        data = decode_cookie(cookie)

        if not data:
            return None

        return data.get("url")

    except Exception as e:
        print(f"[!] Error resolviendo link: {e}")
        return None

def download_mega(link, episode_num):
    try:
        print(f"[+] Descargando episodio {episode_num}...")

        subprocess.run([
            "megadl",
            "--path", f"episodio_{episode_num}.mp4",
            link
        ], check=True)

        print(f"[+] Episodio {episode_num} descargado")

    except subprocess.CalledProcessError:
        print(f"[!] Error descargando episodio {episode_num}")

def main():
    parser = argparse.ArgumentParser(description="AnimeFLV Scraper + Downloader")
    parser.add_argument("-u", "--url", required=True, help="URL del anime")
    parser.add_argument("--no-download", action="store_true", help="Solo obtener links")

    args = parser.parse_args()

    anime_url = args.url
    base_url = get_base_url(anime_url)
    anime_name = get_anime_name(anime_url)

    output_file = f"{anime_name}-mega.txt"

    session = requests.Session()

    episodes = get_episode_list(session, anime_url, base_url)

    print("\n[+] Procesando episodios...\n")

    with open(output_file, "w", encoding="utf-8") as f:

        f.write(f"Anime: {anime_name}\n")
        f.write("Servidor: MEGA\n\n")

        for ep_num, ep_url in episodes:

            print(f"[+] Episodio {ep_num}")

            mega_page = get_mega_link(session, ep_url)

            if not mega_page:
                print("[!] No tiene link MEGA")
                f.write(f"Episodio {ep_num}: ERROR\n")
                continue

            direct_link = mega_page

            if direct_link:
                print(f"[+] Link: {direct_link}")
                f.write(f"Episodio {ep_num}: {direct_link}\n")

                if not args.no_download:
                    download_mega(direct_link, ep_num)
                    time.sleep(DELAY_DOWNLOADS)

            else:
                print("[!] No se pudo resolver")
                f.write(f"Episodio {ep_num}: ERROR\n")

            time.sleep(DELAY_EPISODES)

    print(f"\n[+] Links guardados en {output_file}")

if __name__ == "__main__":
    main()
