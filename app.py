import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random
from io import BytesIO
import numpy as np
from PIL import Image, ImageDraw
import os
import urllib.request

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador de Nubes", page_icon="☁️", layout="wide")

st.title("☁️ Generador de Nubes de Palabras Pro")
st.markdown("Personaliza la forma de tu nube, elige entre 15 tipografías distintas y ajusta tus colores.")

# --- DESCARGA AUTOMÁTICA DE FUENTES ---
@st.cache_resource(show_spinner=False)
def load_fonts():
    fonts_dir = "fonts"
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
    
    # 15 Fuentes seleccionadas de Google Fonts
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
                continue # Si falla una, pasa a la siguiente
        if os.path.exists(path):
            font_paths[name] = path
            
    return font_paths

available_fonts = load_fonts()

# --- GENERADOR DE MÁSCARAS (FORMAS) ---
def get_mask(shape_name):
    if shape_name == "Cuadrada":
        return None # WordCloud por defecto es cuadrado/rectangular
        
    # Crear un lienzo en blanco (800x800)
    mask = Image.new("L", (800, 800), 255)
    draw = ImageDraw.Draw(mask)
    
    if shape_name == "Circular":
        draw.ellipse((50, 50, 750, 750), fill=0)
    
    elif shape_name == "Triangular":
        draw.polygon([(400, 50), (50, 750), (750, 750)], fill=0)
        
    elif shape_name == "Nube":
        # Construimos una nube superponiendo círculos
        draw.ellipse((250, 150, 550, 450), fill=0)
        draw.ellipse((100, 300, 400, 600), fill=0)
        draw.ellipse((400, 300, 700, 600), fill=0)
        draw.ellipse((200, 400, 600, 650), fill=0)
        
    return np.array(mask)

# --- BARRA LATERAL (Configuración) ---
st.sidebar.header("🎨 Configuración Visual")

# Opciones Tipográficas y de Forma
st.sidebar.subheader("Estilo")
font_choice = st.sidebar.selectbox("Tipo de Letra", options=list(available_fonts.keys()))
shape_choice = st.sidebar.selectbox("Forma del Contorno", ["Nube", "Circular", "Cuadrada", "Triangular"])

# Paleta de colores
st.sidebar.subheader("Paleta de Colores")
col1, col2 = st.sidebar.columns(2)
with col1:
    color_1 = st.color_picker("Color 1", "#FF4B4B")
    color_2 = st.color_picker("Color 2", "#FFA421")
with col2:
    color_3 = st.color_picker("Color 3", "#00C246")
    color_4 = st.color_picker("Color 4", "#00A1F1")

bg_color = st.sidebar.color_picker("Color de Fondo", "#0E1117")

# Ajustes de la nube
st.sidebar.subheader("Ajustes")
max_words = st.sidebar.slider("Máximo de palabras", min_value=10, max_value=1000, value=300)

# --- ÁREA PRINCIPAL ---
text_input = st.text_area("✍️ Ingresa o pega tu texto aquí:", height=200, 
                          placeholder="Pega el texto del que quieres generar tu obra de arte...")

def custom_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    colors = [color_1, color_2, color_3, color_4]
    return random.choice(colors)

if st.button("🚀 Generar Nube de Palabras", type="primary"):
    if text_input.strip() == "":
        st.warning("Por favor, ingresa algún texto para generar la nube.")
    else:
        with st.spinner("Creando la magia..."):
            
            # Obtener datos seleccionados
            mask_array = get_mask(shape_choice)
            font_path = available_fonts.get(font_choice, None)
            
            # Generar la nube
            wc = WordCloud(
                width=800, 
                height=800,
                background_color=bg_color,
                max_words=max_words,
                mask=mask_array,
                font_path=font_path,
                color_func=custom_color_func,
                collocations=False,
                contour_width=3 if shape_choice != "Cuadrada" else 0, # Agrega un contorno a la forma
                contour_color=color_1
            ).generate(text_input)

            # Crear figura
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            fig.patch.set_facecolor(bg_color)
            
            # Mostrar
            st.pyplot(fig)

            # Descargar
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches='tight', facecolor=bg_color)
            byte_im = buf.getvalue()

            st.download_button(
                label=f"📥 Descargar Nube {shape_choice} en Alta Resolución",
                data=byte_im,
                file_name=f"nube_{shape_choice.lower()}.png",
                mime="image/png"
            )
