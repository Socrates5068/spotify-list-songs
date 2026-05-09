import json
import os

# Configuración de rutas
ruta_mp3 = r"E:\Music\Spotify\misc"
archivo_json = "tracks.json"
archivo_faltantes = "faltantes.json"

def limpiar_nombre(texto):
    """Limpia caracteres especiales para facilitar la comparación"""
    return "".join(filter(str.isalnum, texto)).lower()

def generar_lista_faltantes():
    # 1. Cargar el JSON con la playlist actualizada
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos_json = json.load(f)
            playlist = datos_json.get('tracks', [])
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_json}")
        return

    # 2. Escanear los archivos .mp3 en tu disco duro
    # Creamos un set con los nombres de archivo limpios para una búsqueda rápida
    archivos_locales = set()
    for nombre_archivo in os.listdir(ruta_mp3):
        if nombre_archivo.lower().endswith(".mp3"):
            # Quitamos la extensión .mp3 para comparar
            nombre_sin_ext = os.path.splitext(nombre_archivo)[0]
            archivos_locales.add(limpiar_nombre(nombre_sin_ext))

    # 3. Comparar y encontrar faltantes
    canciones_faltantes = []
    
    for track in playlist:
        titulo = track.get('title', '')
        artista = track.get('artist', '')
        
        # Intentamos buscar por combinaciones comunes de nombre de archivo
        # Ejemplo: "Artista - Titulo" o "Titulo"
        busqueda_1 = limpiar_nombre(f"{artista}{titulo}")
        busqueda_2 = limpiar_nombre(f"{titulo}{artista}")
        busqueda_3 = limpiar_nombre(titulo)

        encontrada = False
        for archivo in archivos_locales:
            if busqueda_3 in archivo or busqueda_1 in archivo:
                encontrada = True
                break
        
        if not encontrada:
            canciones_faltantes.append(track)

    # 4. Guardar el nuevo JSON con los faltantes
    with open(archivo_faltantes, 'w', encoding='utf-8') as f:
        json.dump({"tracks_faltantes": canciones_faltantes}, f, indent=4, ensure_ascii=False)

    print(f"Proceso finalizado. Se encontraron {len(canciones_faltantes)} canciones faltantes.")
    print(f"Lista guardada en: {archivo_faltantes}")

if __name__ == "__main__":
    generar_lista_faltantes()