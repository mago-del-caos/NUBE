import streamlit as st
from wordcloud import WordCloud
import random
from io import BytesIO
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import urllib.request

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Nube Juventud", page_icon="☁️", layout="wide")

# --- LOGO EN EL ENCABEZADO ---
if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
else:
    st.info("💡 Sube un archivo 'logo.png' a tu repositorio para que aparezca aquí como encabezado.")

st.title("☁️ Nube Juventud")
st.markdown("Generador de nubes de palabras oficial. Compara formas y tipografías, y añade encabezados personalizados.")

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

# --- GENERADOR DE MÁSCARAS (FORMAS PREDEFINIDAS) ---
def get_mask(shape_name):
    mask = Image.new("L", (800, 800), 255)
    draw = ImageDraw.Draw(mask)
    
    if shape_name == "Nube Clásica":
        draw.ellipse((200, 300, 600, 600), fill=0)
        draw.ellipse((100, 350, 300, 550), fill=0)
        draw.ellipse((500, 350, 700, 550), fill=0)
        draw.ellipse((250, 150, 450, 450), fill=0)
        draw.ellipse((350, 200, 550, 450), fill=0)
    elif shape_name == "Nube Esponjosa":
        draw.ellipse((200, 250, 600, 650), fill=0) 
        draw.ellipse((100, 400, 300, 600), fill=0)
        draw.ellipse((500, 400, 700, 600), fill=0)
        draw.ellipse((250, 150, 450, 450), fill=0)
        draw.ellipse((350, 180, 550, 480), fill=0)
        draw.ellipse((150, 250, 350, 450), fill=0)
        draw.ellipse((450, 250, 650, 450), fill=0)
    elif shape_name == "Nube Alargada":
        draw.ellipse((150, 300, 650, 500), fill=0) 
        draw.ellipse((50, 350, 250, 500), fill=0)
        draw.ellipse((550, 350, 750, 500), fill=0)
        draw.ellipse((200, 200, 400, 400), fill=0)
        draw.ellipse((400, 220, 600, 420), fill=0)
    elif shape_name == "Nube Tormenta":
        draw.rectangle((150, 450, 650, 550), fill=0)
        draw.ellipse((100, 400, 250, 550), fill=0)
        draw.ellipse((550, 400, 700, 550), fill=0)
        draw.ellipse((200, 300, 450, 550), fill=0)
        draw.ellipse((350, 250, 600, 550), fill=0)
    elif shape_name == "Cuadrada":
        draw.rectangle((50, 50, 750, 750), fill=0)
    elif shape_name == "Circular":
        draw.ellipse((50, 50, 750, 750), fill=0)
    elif shape_name == "Triangular":
        draw.polygon([(400, 50), (50, 750), (750, 750)], fill=0)
    elif shape_name == "Estrella":
        draw.polygon([(400, 50), (490, 270), (750, 270), (540, 430), (620, 680), (400, 510), (180, 680), (260, 430), (50, 270), (310, 270)], fill=0)
    elif shape_name == "Corazón":
        draw.ellipse((150, 150, 450, 450), fill=0)
        draw.ellipse((350, 150, 650, 450), fill=0)
        draw.polygon([(170, 350), (630, 350), (400, 700)], fill=0)
    elif shape_name == "Diamante":
        draw.polygon([(400, 50), (750, 400), (400, 750), (50, 400)], fill=0)
    elif shape_name == "Hexágono":
        draw.polygon([(400, 50), (700, 225), (700, 575), (400, 750), (100, 575), (100, 225)], fill=0)
        
    return np.array(mask)

# --- BARRA LATERAL (Configuración) ---
st.sidebar.header("⚙️ Configuración Visual")

# 1. Forma de la Nube
st.sidebar.subheader("1. Formas (Hasta 4)")
opciones_formas = ["Nube Clásica", "Nube Esponjosa", "Nube Alargada", "Nube Tormenta", "Circular", "Cuadrada", "Triangular", "Estrella", "Corazón", "Diamante", "Hexágono"]
shape_choices = st.sidebar.multiselect(
    "Compara distintos contornos:", 
    options=opciones_formas,
    default=["Nube Clásica"],
    max_selections=4
)

# 2. Tipografías
st.sidebar.subheader("2. Tipografías")
font_options = list(available_fonts.keys())
default_font = ["Roboto"] if "Roboto" in font_options else ([font_options[0]] if font_options else [])
font_choices = st.sidebar.multiselect(
    "Elige las fuentes a comparar:", 
    options=font_options, 
    default=default_font
)

if not font_options:
    st.sidebar.warning("⚠️ Problema de red descargando fuentes. Reinicia la app en Streamlit.")

# 3. Título de la Imagen
st.sidebar.subheader("3. Título de la Imagen")
image_title = st.sidebar.text_input("Escribe un encabezado (opcional):", "")
title_color = st.sidebar.color_picker("Color del Encabezado", "#FFFFFF")

# 4. Colores de la Nube y Contorno
st.sidebar.subheader("4. Fondos y Contorno")
col_bg1, col_bg2 = st.sidebar.columns(2)
with col_bg1:
    bg_exterior = st.color_picker("Exterior (Fondo)", "#0E1117")
    bg_interior = st.color_picker("Interior (Nube)", "#262730")
with col_bg2:
    contour_color = st.color_picker("Color Contorno", "#FFFFFF")
    contour_width = st.slider("Ancho Contorno", 0, 15, 3)

# 5. Paleta de Palabras
st.sidebar.subheader("5. Colores de Palabras")
num_colors = st.sidebar.number_input("¿Cuántos colores usar?", min_value=1, max_value=10, value=4)
selected_colors = []
color_cols = st.sidebar.columns(2)
default_hex = ["#FF4B4B", "#FFA421", "#00C246", "#00A1F1", "#9D00FF", "#FF007F", "#FFD700", "#00FFFF", "#8B4513", "#808080"]

for i in range(int(num_colors)):
    with color_cols[i % 2]:
        color = st.color_picker(f"Color {i+1}", default_hex[i % len(default_hex)], key=f"color_{i}")
        selected_colors.append(color)

# 6. Ajustes Extra
st.sidebar.subheader("6. Densidad")
max_words = st.sidebar.slider("Máximo de palabras", min_value=50, max_value=2000, value=300)

# --- ÁREA PRINCIPAL ---
text_input = st.text_area("✍️ Ingresa o pega tu texto aquí:", height=150, 
                          placeholder="Pega el texto del que quieres extraer las palabras...")

def get_custom_color_func(colors):
    def custom_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return random.choice(colors)
    return custom_color_func

if st.button("🚀 Generar Nube Juventud", type="primary"):
    if text_input.strip() == "":
        st.warning("⚠️ Por favor, ingresa algún texto.")
    elif len(font_choices) == 0:
        st.warning("⚠️ Selecciona al menos un tipo de letra en la barra lateral.")
    elif len(shape_choices) == 0:
        st.warning("⚠️ Selecciona al menos una forma en la barra lateral.")
    else:
        total_variantes = len(shape_choices) * len(font_choices)
        with st.spinner(f"Generando {total_variantes} combinaciones... ¡Creando la magia!"):
            
            st.success(f"✅ ¡Completado! Aquí tienes tus {total_variantes} diseño(s).")
            grid_cols = st.columns(2)
            
            idx = 0
            for shape_name in shape_choices:
                mask_array = get_mask(shape_name)
                
                for font_name in font_choices:
                    font_path = available_fonts.get(font_name, None)
                    
                    # Generar la nube base
                    wc = WordCloud(
                        width=800, 
                        height=800,
                        background_color=bg_interior, 
                        mode="RGB",                   
                        max_words=max_words,
                        mask=mask_array,
                        font_path=font_path,
                        color_func=get_custom_color_func(selected_colors),
                        collocations=False,
                        contour_width=contour_width,
                        contour_color=contour_color
                    ).generate(text_input)

                    wc_image = wc.to_image()

                    # --- COMPOSICIÓN DEL LIENZO FINAL CON O SIN TÍTULO ---
                    canvas_w = 800
                    y_offset = 120 if image_title.strip() else 0
                    canvas_h = 800 + y_offset
                    
                    final_canvas = Image.new("RGB", (canvas_w, canvas_h), bg_exterior)
                    
                    # Dibujar el texto si existe
                    if image_title.strip():
                        draw = ImageDraw.Draw(final_canvas)
                        try:
                            # Intentamos usar la misma fuente de la nube para el título
                            title_font = ImageFont.truetype(font_path, 60)
                        except:
                            title_font = ImageFont.load_default()
                        
                        # Centrar el texto en el espacio superior
                        bbox = draw.textbbox((0, 0), image_title.strip(), font=title_font)
                        text_w = bbox[2] - bbox[0]
                        text_x = (canvas_w - text_w) / 2
                        
                        draw.text((text_x, 25), image_title.strip(), fill=title_color, font=title_font)

                    # Pegar la nube debajo del título (o en el tope si no hay título)
                    paste_mask = Image.fromarray((255 - mask_array).astype(np.uint8))
                    final_canvas.paste(wc_image, (0, y_offset), paste_mask)

                    # Mostrar en la cuadrícula web
                    with grid_cols[idx % 2]:
                        st.markdown(f"### {shape_name} + {font_name}")
                        st.image(final_canvas, use_container_width=True)
                        
                        buf = BytesIO()
                        final_canvas.save(buf, format="PNG")
                        byte_im = buf.getvalue()

                        st.download_button(
                            label=f"📥 Descargar",
                            data=byte_im,
                            file_name=f"NubeJuventud_{shape_name.replace(' ', '')}_{font_name.replace(' ', '')}.png",
                            mime="image/png",
                            key=f"dl_{shape_name}_{font_name}_{idx}"
                        )
                    idx += 1
