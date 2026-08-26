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

# --- LOGO EN EL ENCABEZADO ---
# Verifica si el archivo logo.png existe en el repositorio
if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
else:
    st.info("💡 Sube un archivo llamado 'logo.png' a tu repositorio en GitHub para que aparezca aquí como encabezado.")

st.title("☁️ Generador de Nubes de Palabras Ultra")
st.markdown("Sube tus propias siluetas, ajusta colores dinámicos y compara múltiples tipos de letra al instante.")

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

# --- GENERADOR DE MÁSCARAS (FORMAS) ---
def get_mask(shape_name):
    if shape_name == "Cuadrada":
        return None 
        
    mask = Image.new("L", (800, 800), 255)
    draw = ImageDraw.Draw(mask)
    
    if shape_name == "Circular":
        draw.ellipse((50, 50, 750, 750), fill=0)
    
    elif shape_name == "Triangular":
        draw.polygon([(400, 50), (50, 750), (750, 750)], fill=0)
        
    elif shape_name == "Nube Mejorada":
        draw.ellipse((200, 300, 600, 600), fill=0)
        draw.ellipse((100, 350, 300, 550), fill=0)
        draw.ellipse((500, 350, 700, 550), fill=0)
        draw.ellipse((250, 150, 450, 450), fill=0)
        draw.ellipse((350, 200, 550, 450), fill=0)
        
    return np.array(mask)

# --- BARRA LATERAL (Configuración) ---
st.sidebar.header("⚙️ Configuración Visual")

# 1. Selector de Fuentes Múltiples (A prueba de fallos de red)
st.sidebar.subheader("Tipografías")
font_options = list(available_fonts.keys())
default_font = ["Roboto"] if "Roboto" in font_options else ([font_options[0]] if font_options else [])

font_choices = st.sidebar.multiselect(
    "Elige los tipos de letra (Generaremos una nube por cada letra para comparar)", 
    options=font_options, 
    default=default_font
)

if not font_options:
    st.sidebar.warning("⚠️ Hubo un problema de red al descargar las fuentes. Reinicia la app desde Streamlit para reintentar.")

# 2. Selector de Formas e Imágenes Propias
st.sidebar.subheader("Forma / Silueta")
shape_choice = st.sidebar.selectbox("Elige la forma de la nube", ["Nube Mejorada", "Circular", "Cuadrada", "Triangular", "🎨 Subir mi propia silueta"])

uploaded_mask = None
if shape_choice == "🎨 Subir mi propia silueta":
    st.sidebar.info("💡 Sube una imagen con fondo blanco. Las palabras rellenarán las partes oscuras de la imagen.")
    uploaded_mask = st.sidebar.file_uploader("Sube tu silueta (PNG, JPG)", type=["png", "jpg", "jpeg"])

# 3. Colores Dinámicos
st.sidebar.subheader("Paleta de Colores")
num_colors = st.sidebar.number_input("¿Cuántos colores quieres usar?", min_value=1, max_value=10, value=4)
selected_colors = []
color_cols = st.sidebar.columns(2)
default_hex = ["#FF4B4B", "#FFA421", "#00C246", "#00A1F1", "#9D00FF", "#FF007F", "#FFD700", "#00FFFF", "#8B4513", "#808080"]

for i in range(int(num_colors)):
    with color_cols[i % 2]:
        color = st.color_picker(f"Color {i+1}", default_hex[i % len(default_hex)], key=f"color_{i}")
        selected_colors.append(color)

bg_color = st.sidebar.color_picker("Color de Fondo", "#0E1117")

# Ajustes Extra
st.sidebar.subheader("Densidad")
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
    elif shape_choice == "🎨 Subir mi propia silueta" and uploaded_mask is None:
        st.warning("⚠️ Has elegido subir tu propia silueta. Por favor, sube una imagen en la barra lateral para continuar.")
    else:
        with st.spinner("Procesando siluetas, colores y letras... ¡Creando la magia!"):
            
            # --- PROCESAR LA FORMA ---
            mask_array = None
            if shape_choice == "🎨 Subir mi propia silueta":
                img = Image.open(uploaded_mask).convert("L")
                img = img.resize((1000, int(1000 * img.height / img.width)))
                m_array = np.array(img)
                mask_array = np.where(m_array > 128, 255, 0).astype(np.uint8)
            else:
                mask_array = get_mask(shape_choice)

            # --- GENERAR LAS NUBES ---
            st.success(f"✅ ¡Completado! Se generaron {len(font_choices)} variante(s).")
            
            grid_cols = st.columns(2)
            
            for idx, font_name in enumerate(font_choices):
                font_path = available_fonts.get(font_name, None)
                
                wc = WordCloud(
                    width=800, 
                    height=800 if mask_array is None else mask_array.shape[0],
                    background_color=bg_color,
                    max_words=max_words,
                    mask=mask_array,
                    font_path=font_path,
                    color_func=get_custom_color_func(selected_colors),
                    collocations=False
                ).generate(text_input)

                fig, ax = plt.subplots(figsize=(8, 8))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                fig.patch.set_facecolor(bg_color)
                
                buf = BytesIO()
                fig.savefig(buf, format="png", dpi=300, bbox_inches='tight', facecolor=bg_color)
                byte_im = buf.getvalue()

                with grid_cols[idx % 2]:
                    st.markdown(f"### Letra: {font_name}")
                    st.pyplot(fig)
                    st.download_button(
                        label=f"📥 Descargar nube ({font_name})",
                        data=byte_im,
                        file_name=f"nube_{font_name.lower().replace(' ', '_')}.png",
                        mime="image/png",
                        key=f"dl_{font_name}"
                    )
