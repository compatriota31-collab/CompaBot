import streamlit as st
from openai import OpenAI
import base64


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# =========================
# FONDO
# =========================

def fondo_local(imagen):
    try:
        with open(imagen, "rb") as archivo:
            contenido = base64.b64encode(archivo.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{contenido}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            [data-testid="stChatMessage"] {{
                background-color: rgba(255,255,255,0.88);
                padding:12px;
                border-radius:15px;
                margin-bottom:10px;
            }}
            h1 {{ color:white; text-shadow:2px 2px 6px black; }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        pass  # Si no hay fondo, continúa sin error

fondo_local("fondo.png")

# =========================
# MEMORIA
# =========================

if "chat" not in st.session_state:
    st.session_state.chat = []

if "personaje" not in st.session_state:
    st.session_state.personaje = None

# =========================
# PERSONAJES
# =========================

personajes = {
    "urracá": "Urracá",
    "urraca": "Urracá",
    "maría de la ossa": "María de la Ossa",
    "maria de la ossa": "María de la Ossa",
    "maria de la osa": "María de la Ossa",
    "manuel amador": "Manuel Amador Guerrero",
    "amador guerrero": "Manuel Amador Guerrero",
    "manuel amador guerrero": "Manuel Amador Guerrero",
    "belisario porras": "Belisario Porras",
    "victoriano lorenzo": "Victoriano Lorenzo",
    "justo arosemena": "Justo Arosemena"
}

# =========================
# TITULO
# =========================

st.title("CompaBot")
st.info("Conversa con personajes históricos de Panamá.")

# =========================
# INPUT
# =========================

mensaje = st.chat_input("Escribe un personaje o pregunta")

# =========================
# PROCESAR MENSAJE
# =========================

if mensaje:

    # --- Detectar si están eligiendo personaje ---
    nombre_lower = mensaje.lower().strip()
    if nombre_lower in personajes:
        st.session_state.personaje = personajes[nombre_lower]
        st.session_state.chat = []  # Reinicia el chat al cambiar personaje

    elif st.session_state.personaje is None:
        # Si no hay personaje aún, asume que el texto es el nombre del personaje
        st.session_state.personaje = mensaje.strip()
        st.session_state.chat = []

    # --- Guardar mensaje del usuario ---
    st.session_state.chat.append({
        "role": "user",
        "content": mensaje
    })

    personaje_actual = st.session_state.personaje

    # --- System prompt ---
    system_prompt = f"""Eres {personaje_actual}, un personaje histórico de Panamá.

REGLAS IMPORTANTES:
- Habla SIEMPRE en primera persona como {personaje_actual}.
- Mantente completamente en personaje en toda la conversación.
- Solo habla sobre historia de Panamá y tu vida como {personaje_actual}.
- No inventes hechos históricos falsos. Si no sabes algo, dilo con humildad.
- Responde de manera educativa, natural y amigable, como si estuvieras hablando con un estudiante.
- Nunca digas que eres una IA o un modelo de lenguaje.
- Responde siempre en español."""

    # --- Construir historial completo para la API ---
    mensajes_api = [{"role": "system", "content": system_prompt}]
    mensajes_api += st.session_state.chat  # incluye TODO el historial

    # --- Llamada a la API ---
    try:
        respuesta = client.chat.completions.create(
            model="openrouter/auto",
            messages=mensajes_api
        )
        texto = respuesta.choices[0].message.content

    except Exception as e:
        texto = f"⚠️ Error al conectar con el servidor: {str(e)}\n\nIntenta nuevamente en unos segundos."

    # --- Guardar respuesta ---
    st.session_state.chat.append({
        "role": "assistant",
        "content": texto
    })

# =========================
# MOSTRAR CHAT
# =========================

for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# =========================
# PERSONAJE ACTUAL
# =========================

if st.session_state.personaje:
    st.success(f"🎭 Personaje actual: {st.session_state.personaje}")

# =========================
# BOTON RESET
# =========================

if st.button("Cambiar personaje"):
    st.session_state.chat = []
    st.session_state.personaje = None
    st.rerun()
