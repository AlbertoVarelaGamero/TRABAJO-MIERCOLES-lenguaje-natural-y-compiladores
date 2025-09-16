# ChronoLogistics - Dashboard Operativo (Streamlit)
# Código revisado para calcular el riesgo automáticamente sin necesidad de pulsar botón.
# Ejecuta con: streamlit run dashboard.py

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import io
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(page_title="ChronoLogistics - Dashboard Operativo", layout="wide")

def generar_mapa_calor(seed=0, n_clusters=6):
    rng = np.random.RandomState(seed)
    data = rng.rand(200, 200)
    for _ in range(n_clusters):
        x = rng.randint(20, 180)
        y = rng.randint(20, 180)
        amp = rng.uniform(0.6, 1.0)
        sx = rng.uniform(6, 18)
        sy = rng.uniform(6, 18)
        xv, yv = np.meshgrid(np.arange(200), np.arange(200))
        data += amp * np.exp(-(((xv - x) ** 2) / (2 * sx ** 2) + ((yv - y) ** 2) / (2 * sy ** 2)))
    data = (data - data.min()) / data.max()
    flat = data.flatten()
    idx_sorted = np.argsort(flat)[-n_clusters:]
    coords = [(i % 200, i // 200) for i in idx_sorted]
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(data, cmap='hot')
    ax.axis('off')
    top3 = coords[-3:][::-1]
    for i, (cx, cy) in enumerate(top3, start=1):
        ax.scatter(cx, cy, s=120, facecolors='none', edgecolors='cyan', linewidths=2)
        ax.text(cx + 5, cy + 5, f'{i}', color='cyan', fontsize=12, weight='bold')
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf), top3

def generar_gan_image(seed=0, estilo='Fortaleza Verde'):
    rng = np.random.RandomState(seed)
    arr = np.clip(rng.normal(0.5, 0.25, (256, 256, 3)), 0, 1)
    if estilo == 'Fortaleza Verde':
        arr[..., 0] *= 0.6
        arr[..., 1] *= 1.2
    else:
        arr[..., 2] *= 1.2
    img = Image.fromarray(np.uint8(arr * 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 220), (256, 256)], fill=(0, 0, 0, 120))
    draw.text((6, 224), estilo, fill=(255, 255, 255))
    return img

def precog_predecir_riesgo(velocidad_media, intensidad_lluvia, humedad, top3_strength=0.0):
    base = 0.25 * velocidad_media + 0.4 * intensidad_lluvia + 0.2 * humedad
    score = base / (0.25 * 150 + 0.4 * 200 + 0.2 * 100) * 100
    score *= 1 + 0.5 * top3_strength
    return float(np.clip(score, 0, 100))

def interpretar_riesgo(percent):
    if percent < 40:
        return f"{percent:.0f}% - BAJO"
    elif percent < 70:
        return f"{percent:.0f}% - MEDIO"
    elif percent < 90:
        return f"{percent:.0f}% - ALTO"
    else:
        return f"{percent:.0f}% - CRÍTICO"

st.title("ChronoLogistics — Dashboard Operativo (War Room)")
st.markdown("**Unidad de Estrategia y Respuesta a Crisis de IA — DEMO FUNCIONAL**")

tabs = st.tabs(["Precog: Monitor de Riesgo Táctico", "Chronos: Visión Estratégica 2040", "K-Lang: Manual de Batalla Interactivo"])

with tabs[0]:
    st.header("Precog — Monitor de Riesgo Táctico")
    col1, col2 = st.columns([2, 1])
    with col1:
        seed = st.number_input("Semilla del mapa", value=42)
        mapa_img, top3 = generar_mapa_calor(seed=int(seed))
        st.image(mapa_img, use_column_width=True, caption="Mapa de clústeres")
    with col2:
        velocidad_media = st.slider("Velocidad media (km/h)", 0, 150, 40)
        intensidad_lluvia = st.slider("Intensidad de lluvia (mm/h)", 0, 200, 10)
        humedad = st.slider("Humedad (%)", 0, 100, 50)
        top3_strength = len(top3) / 3.0
        percent = precog_predecir_riesgo(velocidad_media, intensidad_lluvia, humedad, top3_strength)
        st.metric(label="Nivel de Riesgo en Cascada", value=interpretar_riesgo(percent), delta=f"{percent:.1f}%")

with tabs[1]:
    st.header("Chronos — Visión Estratégica 2040")
    strategy = st.selectbox("Selecciona la estrategia", ["Fortaleza Verde", "Búnker Tecnológico"])
    img = generar_gan_image(seed=123 if strategy == "Fortaleza Verde" else 321, estilo=strategy)
    st.image(img, caption=f"Visualizador de Futuros: {strategy}", use_column_width=True)
    if strategy == "Fortaleza Verde":
        st.markdown("**Beneficios:** Infraestructuras resilientes, menor impacto climático, incentivos fiscales.")
    else:
        st.markdown("**Beneficios:** Redundancia tecnológica, continuidad operativa, ventaja competitiva.")

with tabs[2]:
    st.header("K-Lang — Manual de Batalla Interactivo")
    protocols = {
        'VÍSPERA': {'trigger': 'VIENTO > 60 km/h', 'actions': ['Notificar equipo', 'Preparar recursos']},
        'CÓDIGO ROJO': {'trigger': 'VIENTO > 90 km/h o INUNDACIÓN > 50 cm', 'actions': ['Activar emergencia', 'Aislar activos']},
        'RENACIMIENTO': {'trigger': 'FASE DE RECUPERACIÓN', 'actions': ['Evaluar daños', 'Reparar']} }
    sel = st.selectbox("Selecciona protocolo", list(protocols.keys()))
    st.markdown(f"**Disparador:** {protocols[sel]['trigger']}")
    for act in protocols[sel]['actions']:
        st.write(f"- {act}")
    sim_viento = st.slider("Velocidad del Viento (km/h)", 0, 150, 30)
    sim_inund = st.slider("Nivel de Inundación (cm)", 0, 300, 5)
    active_protocol = 'VÍSPERA'
    if sim_viento >= 90 or sim_inund >= 50:
        active_protocol = 'CÓDIGO ROJO'
        st.error(f"PROTOCOLO ACTIVO: {active_protocol}")
    elif sim_viento < 20 and sim_inund < 5:
        active_protocol = 'RENACIMIENTO'
        st.success(f"ESTADO NORMAL: {active_protocol}")
    else:
        st.warning(f"PROTOCOLO POTENCIAL: {active_protocol}")

st.sidebar.title("Cómo ejecutar")
st.sidebar.markdown("1. Guarda este archivo como `dashboard.py`\n2. Instala dependencias: `pip install streamlit numpy matplotlib pillow`\n3. Ejecuta: `streamlit run dashboard.py`\n4. Abre el enlace que aparece en la terminal en tu navegador para usar el dashboard.")
