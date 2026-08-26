import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Generador de Nubes de Palabras", page_icon="☁️", layout="wide")

st.title("☁️ Generador de Nubes de Palabras")
st.markdown("Crea visualizaciones de texto de alta calidad y personaliza la paleta de colores a tu gusto.")

# --- BARRA LATERAL (Configuración) ---
st.sidebar.header("🎨 Configuración Visual")

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
st.sidebar.subheader("Ajustes de la Nube")
max_words = st.sidebar.slider("Máximo de palabras", min_value=10, max_value=1000, value=200)
width = st.sidebar.slider("Ancho (px)", min_value=800, max_value=2000, value=1200)
height = st.sidebar.slider("Alto (px)", min_value=600, max_value=1600, value=800)

# --- ÁREA PRINCIPAL ---
text_input = st.text_area("✍️ Ingresa o pega tu texto aquí:", height=200, 
                          placeholder="Escribe el texto del cual quieres extraer las palabras más frecuentes...")

# Función para colorear las palabras con la paleta elegida
def custom_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    colors = [color_1, color_2, color_3, color_4]
    return random.choice(colors)

if st.button("🚀 Generar Nube de Palabras", type="primary"):
    if text_input.strip() == "":
        st.warning("Por favor, ingresa algún texto para generar la nube.")
    else:
        with st.spinner("Creando la magia..."):
            # Generar la nube de palabras
            wc = WordCloud(
                width=width, 
                height=height,
                background_color=bg_color,
                max_words=max_words,
                color_func=custom_color_func,
                collocations=False # Evita que se repitan palabras compuestas
            ).generate(text_input)

            # Crear la figura con Matplotlib
            fig, ax = plt.subplots(figsize=(width/100, height/100))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            fig.patch.set_facecolor(bg_color)
            
            # Mostrar en Streamlit
            st.pyplot(fig)

            # Preparar imagen para descargar
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches='tight', facecolor=bg_color)
            byte_im = buf.getvalue()

            st.download_button(
                label="📥 Descargar Imagen en Alta Resolución",
                data=byte_im,
                file_name="nube_de_palabras.png",
                mime="image/png"
            )
