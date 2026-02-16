import random
from io import BytesIO

import requests
import streamlit as st
from PIL import Image

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "https://pokeapi.co/api/v2/"
IMAGE_SIZE = 300
CORRECT_POINTS = 100
WRONG_POINTS = -100
MAX_ATTEMPTS = 3

GENERATION_RANGES = {
    "Gen 1 (Kanto)": (1, 151),
    "Gen 1-2": (1, 251),
    "Gen 1-3": (1, 386),
    "Gen 1-4": (1, 493),
    "Gen 1-5": (1, 649),
    "Gen 1-6": (1, 721),
    "Gen 1-7": (1, 809),
    "Gen 1-8": (1, 905),
    "All Pokémon": (1, 1010),
}

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "score" not in st.session_state:
    st.session_state.score = 0
if "current_pokemon" not in st.session_state:
    st.session_state.current_pokemon = None
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "gen_range" not in st.session_state:
    st.session_state.gen_range = (1, 151)
if "message" not in st.session_state:
    st.session_state.message = ""
if "message_type" not in st.session_state:
    st.session_state.message_type = ""

# ============================================================================
# FUNCTIONS
# ============================================================================


def get_pokemon_info(pokemon_id):
    """Fetch Pokémon data from the PokéAPI."""
    url = f"{BASE_URL}pokemon/{pokemon_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def new_pokemon():
    """Load a random Pokémon from the current generation range."""
    st.session_state.attempts = 0
    st.session_state.message = ""

    pokemon_id = random.randint(
        st.session_state.gen_range[0], st.session_state.gen_range[1]
    )
    st.session_state.current_pokemon = get_pokemon_info(pokemon_id)

    if st.session_state.current_pokemon is None:
        new_pokemon()


def check_answer(user_input):
    """Check if the user's guess is correct."""
    if not user_input:
        return

    pokemon = st.session_state.current_pokemon
    correct_answer = pokemon["name"].lower().split("-")[0]
    user_input = user_input.lower().strip()

    if user_input == correct_answer:
        st.session_state.message = f"✅ CORRECT! It was {correct_answer.capitalize()}!"
        st.session_state.message_type = "success"
        st.session_state.score += CORRECT_POINTS
        new_pokemon()
    else:
        st.session_state.attempts += 1

        if st.session_state.attempts >= MAX_ATTEMPTS:
            st.session_state.message = (
                f"❌ Out of attempts! It was {correct_answer.capitalize()}!"
            )
            st.session_state.message_type = "error"
            st.session_state.score += WRONG_POINTS
            new_pokemon()
        else:
            remaining = MAX_ATTEMPTS - st.session_state.attempts
            st.session_state.message = f"❌ Wrong! {remaining} attempt(s) left"
            st.session_state.message_type = "warning"
            st.session_state.score += WRONG_POINTS


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(page_title="Who's That Pokémon?", page_icon="🎮", layout="centered")

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        background-color: #2b2b2b;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# UI LAYOUT
# ============================================================================

# Title
st.markdown(
    "<h1 style='text-align: center; color: #ffcc00;'> Who's That Pokémon? </h1>",
    unsafe_allow_html=True,
)

# Instructions
st.markdown(
    "<p style='text-align: center; color: #e0e0e0;'>Guess the Pokémon's name! You have 3 attempts per Pokémon.</p>",
    unsafe_allow_html=True,
)

# Score display
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    score_color = "#4CAF50" if st.session_state.score >= 0 else "#f44336"
    st.markdown(
        f"<h2 style='text-align: center; color: {score_color};'>Score: {st.session_state.score}</h2>",
        unsafe_allow_html=True,
    )

# Generation selector and reset button
col1, col2 = st.columns([2, 1])
with col1:
    selected_gen = st.selectbox(
        "Generation:", list(GENERATION_RANGES.keys()), index=0, key="gen_selector"
    )
    if st.session_state.gen_range != GENERATION_RANGES[selected_gen]:
        st.session_state.gen_range = GENERATION_RANGES[selected_gen]
        new_pokemon()
        st.rerun()

with col2:
    if st.button("Reset Score"):
        st.session_state.score = 0
        st.session_state.attempts = 0
        new_pokemon()
        st.rerun()

# Load first Pokémon if none exists
if st.session_state.current_pokemon is None:
    new_pokemon()

# Display Pokémon image
pokemon = st.session_state.current_pokemon
sprite_url = pokemon["sprites"]["front_default"]

if sprite_url:
    try:
        img_response = requests.get(sprite_url)
        img = Image.open(BytesIO(img_response.content))
        img_resized = img.resize((IMAGE_SIZE, IMAGE_SIZE))

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(img_resized, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading image: {e}")

# Show feedback message
if st.session_state.message:
    if st.session_state.message_type == "success":
        st.success(st.session_state.message)
    elif st.session_state.message_type == "error":
        st.error(st.session_state.message)
    else:
        st.warning(st.session_state.message)

# Input and buttons
guess = st.text_input(
    "Your guess:",
    key="guess_input",
    label_visibility="collapsed",
    placeholder="Enter Pokémon name and press Enter...",
    on_change=lambda: (
        check_answer(st.session_state.guess_input)
        if st.session_state.guess_input
        else None
    ),
)

# Buttons (outside form)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✓ Submit Answer", use_container_width=True, type="primary"):
        if guess:
            check_answer(guess)
            st.session_state.input_counter += 1
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>Powered by PokéAPI</p>",
    unsafe_allow_html=True,
)
