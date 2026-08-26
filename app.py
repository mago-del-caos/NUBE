import streamlit as st
from wordcloud import WordCloud
import random
from io import BytesIO
import numpy as np
from PIL import Image
import os
import urllib.request

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador de Nubes", page_icon="☁️", layout="wide")

# --- LOGO EN EL ENCABEZADO ---
if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
else:
    st.info("💡 Sube un archivo 'logo.png' a tu repositorio para que aparezca aquí como encabezado.")

st.title("☁️ Generador de Nubes de Palabras Ultra")
st.markdown("Sube tu imagen para definir la forma, controla el contorno y ajusta fondos independientes.")

# --- DESCARGA AUTOMÁTICA DE FUENTES ---
@st.cache_resource(show_spinner=False)
def load_fonts():
    fonts_dir = "fonts"
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
    
    font_urls = {
        "Roboto": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf",
        "Oswald": "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald-Regular.ttf",
        "Lato": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Regular.ttf",
        "Montserrat": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Regular.ttf",
        "Raleway": "https://github.com/google/fonts/raw/main/ofl/raleway/Raleway-Regular.ttf",
        "Merriweather": "https://github.com/google/fonts/raw/main/ofl/merriweather/Merriweather-Regular.ttf",
        "Playfair Display": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Regular.ttf",
        "Ubuntu": "https://github.com/google/fonts/raw/main/ufl/ubuntu/Ubuntu-Regular.ttf",
        "Lora": "https://github.com/google/fonts/raw/main/ofl/lora/Lora-Regular.ttf",
        "Pacifico": "https://github.com/google/fonts/raw/main/ofl/pacifico/Pacifico-Regular.ttf",
        "Caveat": "https://github.com/google/fonts/raw/main/ofl/caveat/Caveat-Regular.ttf",
        "Anton": "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",
        "Dancing Script": "https://github.com/google/fonts/raw/main/ofl/dancingscript/DancingScript-Regular.ttf",
        "Lobster": "https://github.com/google/fonts/raw/main/ofl/lobster/Lobster-Regular.ttf",
        "Inconsolata": "https://github.com/google/fonts/raw/main/ofl/inconsolata/Inconsolata-Regular.ttf"
    }
    
    font_paths = {}
    for name, url in font_urls.items():
        path = os.path.join(fonts_dir, f"{name.replace(' ', '_')}.ttf")
        if not os.path.exists(path):
            try:
                urllib.request.urlretrieve(url, path)
            except Exception:
                continue 
        if os.path.exists(path):
            font_paths[name] = path
            
    return font_paths

available_fonts = load_fonts()

# --- BARRA LATERAL (Configuración) ---
st.sidebar.header("⚙️ Configuración Visual")

# 1. Imagen Base (La nueva máscara obligatoria)
st.sidebar.subheader("1. Forma de la Nube (Imagen)")
st.sidebar.info("💡 Sube una imagen (idealmente con fondo blanco o transparente). Esta será la silueta de tu nube.")
uploaded_mask = st.sidebar.file_uploader("Sube tu imagen (PNG o JPG)", type=["png", "jpg", "jpeg"])

# 2. Tipografías
st.sidebar.subheader("2. Tipografías")
font_options = list(available_fonts.keys())
default_font = ["Roboto"] if "Roboto" in font_options else ([font_options[0]] if font_options else [])
font_choices = st.sidebar.multiselect(
    "Elige las fuentes a comparar", 
    options=font_options, 
    default=default_font
)

if not font_options:
    st.sidebar.warning("⚠️ Problema de red descargando fuentes. Reinicia la app en Streamlit.")

# 3. Colores de la Nube y Contorno
st.sidebar.subheader("3. Fondos y Contorno")
col_bg1, col_bg2 = st.sidebar.columns(2)
with col_bg1:
    bg_exterior = st.color_picker("Exterior (Fondo)", "#0E1117")
    bg_interior = st.color_picker("Interior (Nube)", "#262730")
with col_bg2:
    contour_color = st.color_picker("Color Contorno", "#FFFFFF")
    contour_width = st.slider("Ancho Contorno", 0, 15, 2)

# 4. Paleta de Palabras
st.sidebar.subheader("4. Colores de Palabras")
num_colors = st.sidebar.number_input("¿Cuántos colores usar?", min_value=1, max_value=10, value=4)
selected_colors = []
color_cols = st.sidebar.columns(2)
default_hex = ["#FF4B4B", "#FFA421", "#00C246", "#00A1F1", "#9D00FF", "#FF007F", "#FFD700", "#00FFFF", "#8B4513", "#808080"]

for i in range(int(num_colors)):
    with color_cols[i % 2]:
        color = st.color_picker(f"Color {i+1}", default_hex[i % len(default_hex)], key=f"color_{i}")
        selected_colors.append(color)

# Ajustes Extra
st.sidebar.subheader("5. Densidad")
max_words = st.sidebar.slider("Máximo de palabras", min_value=50, max_value=2000, value=300)

# --- ÁREA PRINCIPAL ---
text_input = st.text_area("✍️ Ingresa o pega tu texto aquí:", height=150, 
                          placeholder="Pega el texto del que quieres generar tu obra de arte...")

def get_custom_color_func(colors):
    def custom_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return random.choice(colors)
    return custom_color_func

if st.button("🚀 Generar Nubes de Palabras", type="primary"):
    if text_input.strip() == "":
        st.warning("⚠️ Por favor, ingresa algún texto para generar la nube.")
    elif len(font_choices) == 0:
        st.warning("⚠️ Selecciona al menos un tipo de letra en la barra lateral.")
    elif uploaded_mask is None:
        st.warning("⚠️ Sube una imagen en la barra lateral para definir la forma de tu nube.")
    else:
        with st.spinner("Construyendo las capas de la imagen... ¡Creando la magia!"):
            
            # --- PROCESAR LA IMAGEN (MÁSCARA) ---
            original_img = Image.open(uploaded_mask)
            
            # Detectar si tiene transparencia (PNG) o si es un JPG con fondo blanco
            if original_img.mode in ('RGBA', 'LA') or (original_img.mode == 'P' and 'transparency' in original_img.info):
                alpha = original_img.convert('RGBA').split()[-1]
                mask_array = 255 - np.array(alpha) # Invertimos el alfa para WordCloud
            else:
                grayscale = original_img.convert("L")
                mask_array = np.where(np.array(grayscale) > 128, 255, 0).astype(np.uint8)

            # Redimensionar la máscara si es muy grande para agilizar el servidor
            if mask_array.shape[1] > 1000:
                scale = 1000 / mask_array.shape[1]
                new_w, new_h = 1000, int(mask_array.shape[0] * scale)
                mask_img = Image.fromarray(mask_array).resize((new_w, new_h), Image.Resampling.LANCZOS)
                mask_array = np.where(np.array(mask_img) > 128, 255, 0).astype(np.uint8)

            height, width = mask_array.shape

            st.success(f"✅ ¡Completado! Se generaron {len(font_choices)} variante(s).")
            grid_cols = st.columns(2)
            
            for idx, font_name in enumerate(font_choices):
                font_path = available_fonts.get(font_name, None)
                
                # Generar la nube con fondo sólido (evita el bug interno de la librería con los contornos)
                wc = WordCloud(
                    width=width, 
                    height=height,
                    background_color=bg_interior, # Usamos el color interior directamente aquí
                    mode="RGB",                   # Modo RGB estándar para que el contorno funcione perfecto
                    max_words=max_words,
                    mask=mask_array,
                    font_path=font_path,
                    color_func=get_custom_color_func(selected_colors),
                    collocations=False,
                    contour_width=contour_width,
                    contour_color=contour_color
                ).generate(text_input)

                wc_image = wc.to_image()

                # --- ENSAMBLAR CAPAS (COMPOSICIÓN INTELIGENTE) ---
                # Capa 1: El lienzo base con el color exterior
                final_canvas = Image.new("RGB", (width, height), bg_exterior)
                
                # Capa 2: Recortamos la nube (que ya tiene el fondo interior) y la pegamos sobre el lienzo
                paste_mask = Image.fromarray((255 - mask_array).astype(np.uint8))
                final_canvas.paste(wc_image, (0, 0), paste_mask)

                with grid_cols[idx % 2]:
                    st.markdown(f"### {font_name}")
                    
                    # Mostrar la imagen terminada directo en Streamlit
                    st.image(final_canvas, use_container_width=True)
                    
                    # Guardar para descarga
                    buf = BytesIO()
                    final_canvas.save(buf, format="PNG")
                    byte_im = buf.getvalue()

                    st.download_button(
                        label=f"📥 Descargar ({font_name})",
                        data=byte_im,
                        file_name=f"nube_{font_name.lower().replace(' ', '_')}.png",
                        mime="image/png",
                        key=f"dl_{font_name}"
                    )
