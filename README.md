# 🎬 AnimeFLV Tool

Script en Python para **extraer enlaces de descarga desde AnimeFLV y descargar automáticamente los episodios desde MEGA**.

---
## 🚀 Características

- Obtiene automáticamente la lista de episodios desde AnimeFLV
- Extrae enlaces de descarga del servidor MEGA
- Guarda los enlaces en un archivo `.txt`
- Descarga los episodios automáticamente
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
python animeflvd.py -u https://www4.animeflv.net/anime/naruto-shippuden
```

Se crearán los directorios correspondientes para los episodios y para los archivos contenedores de los enlaces de descarga:

```
Naruto Shippuden/
└── links/
   ├── Naruto Shippuden - MEGA.txt
   ├── Naruto Shippuden - 1Fichier.txt 
   └── Naruto Shippuden - MEGA.txt
```

---
### 2. Descargar episodios automáticamente (solo MEGA)

```bash
python animeflvd.py -f Naruto\ Shippuden/links/Naruto\ Shippuden\ -\ MEGA.txt
```

Los vídeos serán descargados en formato .mp4 en el directorio creado bajo el nombre del anime:

```
Naruto Shippuden/
├── Naruto Shippuden - Episodio 1.mp4
├── Naruto Shippuden - Episodio 2.mp4
└── Naruto Shippuden - Episodio 3.mp4
└── links/
```

---
## ⚙️ Cómo funciona

1. Accede a la página del anime en AnimeFLV
2. Extrae la lista de episodios desde el JavaScript embebido
3. Entra a cada episodio
4. Obtiene el enlace de descarga
5. Descarga el archivo usando megatools
    
---
## ⚠️ Consideraciones

- MEGA tiene límites de descarga por IP (puede bloquear temporalmente)
- Se recomienda no eliminar los delays del script
- El sitio puede cambiar su estructura en cualquier momento

_____

