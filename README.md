# 🎬 AnimeFLV MEGA Downloader

Script en Python para **extraer enlaces de descarga desde AnimeFLV y descargar automáticamente los episodios desde MEGA**.

---

## 🚀 Características

- Obtiene automáticamente la lista de episodios desde AnimeFLV
- Extrae enlaces de descarga del servidor MEGA
- Evita páginas intermedias (bypass de protección)
- Descarga los episodios automáticamente
- Guarda los enlaces en un archivo `.txt`
- Manejo básico de errores y rate limiting

---

## 🧰 Requisitos

- Python 3.8+
- pip

### Dependencias Python:

```bash
pip install requests beautifulsoup4
````
### Herramienta externa:

Debes instalar:

- megatools
    
#### En Linux:

```bash
sudo apt install megatools
```
---
## ▶️ Uso

### 1. Obtener solo los enlaces

```bash
python animeflvd.py -u https://www4.animeflv.net/anime/nombre-del-anime --no-download
```

---
### 2. Descargar episodios automáticamente

```bash
python animeflvd.py -u https://www4.animeflv.net/anime/nombre-del-anime
```

---
## 📁 Salida

Se genera un archivo `.txt` con los enlaces:

```
nombre-del-anime-mega.txt
```

Ejemplo:

```
Anime: naruto
Servidor: MEGA

Episodio 1: https://mega.nz/xxxx
Episodio 2: https://mega.nz/yyyy
Episodio 3: ERROR
```
---

## ⚙️ Cómo funciona

1. Accede a la página del anime en AnimeFLV
2. Extrae la lista de episodios desde el JavaScript embebido
3. Entra a cada episodio
4. Obtiene el enlace de descarga (MEGA)
5. Resuelve el enlace final mediante cookies
6. Descarga el archivo usando megatools
    

---

## ⚠️ Consideraciones

- MEGA tiene límites de descarga por IP (puede bloquear temporalmente)
- Se recomienda no eliminar los delays del script
- El sitio puede cambiar su estructura en cualquier momento
_____

