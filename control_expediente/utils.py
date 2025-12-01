# utils.py
import unicodedata
import os
from django.utils.text import slugify

def normalize_filename(filename):
    """
    Convierte nombres de archivo con tildes, ñ, espacios y caracteres raros
    a un formato seguro en ASCII.
    Ejemplo: 'Planificación_Áreas.pdf' -> 'planificacion_areas.pdf'
    """
    name, ext = os.path.splitext(filename)

    # Quitar tildes y caracteres especiales
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')

    # Convertir a slug (quita espacios y símbolos)
    name = slugify(name)

    return f"{name}{ext.lower()}"

