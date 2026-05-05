import vtracer
from rembg import remove
from PIL import Image
import io
import os

def png_to_transparent_svg(input_path, output_path):
    print(f"Traitement de : {input_path}...")

    # 1. Suppression du fond avec rembg
    with open(input_path, 'rb') as i:
        input_data = i.read()
        # Retire l'arrière-plan (gère aussi le blanc)
        output_data = remove(input_data)
    
    # On convertit le résultat en objet Image pour manipulation si besoin
    img = Image.open(io.BytesIO(output_data)).convert("RGBA")
    
    # Sauvegarde temporaire pour la vectorisation
    temp_png = "temp_no_bg.png"
    img.save(temp_png)

    # 2. Vectorisation vers SVG
    # vtracer transforme les pixels en tracés mathématiques
    vtracer.convert_image_to_svg(
        temp_png, 
        output_path,
        colormode='color',        # 'color' ou 'binary'
        hierarchical='stacked',    # 'stacked' évite les trous entre les formes
        mode='spline',             # 'spline' pour des courbes lisses
        filter_speckle=4,          # Supprime les petits bruits de pixels
        corner_threshold=60,
        length_threshold=4.0,
        max_iterations=10,
        splice_threshold=45,
        path_precision=2
    )

    # Nettoyage
    if os.path.exists(temp_png):
        os.remove(temp_png)
        
    print(f"Terminé ! Fichier enregistré sous : {output_path}")

# Utilisation
png_to_transparent_svg("ton_image.png", "resultat.svg")