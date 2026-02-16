import random
import tkinter as tk
import tkinter.ttk as ttk
from io import BytesIO

import requests
import sv_ttk
from PIL import Image, ImageTk

# ------ globals
current_pokemon = None  # global declare current pokemon
base_url = "https://pokeapi.co/api/v2/"
player_score = 0
attempts = 0

# Generation Ranges
generation_ranges = {
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

current_gen_range = (1, 151)
# ------------------Tkinter Code ---------------------

root = tk.Tk()
style = ttk.Style(root)

# TK Theme
style.theme_use("clam")
root.title("Who's that Pokemon?")
root.geometry("1000x1200")
root.configure(background="#2b2b2b")

# Title Box
title_label = tk.Label(
    root,
    text="Who's That Pokémon?",
    font=("Arial", 28, "bold"),  # Cleaner font
    bg="#2b2b2b",
    fg="#ffcc00",  # Pokémon yellow
    pady=10,
)
title_label.pack(pady=15)

# Instructions
instructions = tk.Label(
    root,
    text="Guess the Pokémon's name! After 3 wrong guesses, you will be shown a new Pokemon.",
    font=("Arial", 14),
    bg="#2b2b2b",
    fg="#e0e0e0",  # Light gray
)
instructions.pack(pady=5)

# Score Display
score_label = tk.Label(
    root,
    text=f"Score: {player_score}",
    font=("Arial", 22, "bold"),
    bg="#2b2b2b",
    fg="#4CAF50",  # Green for positive vibes
    pady=5,
)
score_label.pack(pady=10)

# Reset Button
reset_button = tk.Button(
    root,
    text="Reset Score",
    font=("Arial", 12, "bold"),
    bg="#ff6b6b",  # Red
    fg="white",
    activebackground="#ff5252",  # Darker red when clicked
    activeforeground="white",
    relief=tk.FLAT,
    borderwidth=0,
    padx=20,
    pady=10,
    cursor="hand2",  # Hand cursor on hover
)
reset_button.pack(pady=5)

# Gen Selector
gen_frame = tk.Frame(root, bg="#2b2b2b")
gen_frame.pack(pady=10)

gen_label = tk.Label(
    gen_frame,
    text="Generation:",
    font=("Arial", 12, "bold"),
    bg="#2b2b2b",
    fg="#e0e0e0",
)

gen_label.pack(side=tk.LEFT, padx=5)

gen_var = tk.StringVar(value="Gen 1 (Kanto)")
gen_dropdown = ttk.Combobox(
    gen_frame,
    textvariable=gen_var,
    values=list(generation_ranges.keys()),
    state="readonly",
    width=18,
    font=("Arial", 11),
)
gen_dropdown.pack(side=tk.LEFT, padx=5)


# Img Display
img_label = tk.Label(root, bg="#2b2b2b")
img_label.pack(pady=20)

# ------------- Poke API --------------------


def get_pokemon_info(id):
    url = f"{base_url}/pokemon/{id}"
    response = requests.get(url)
    if response.status_code == 200:
        pokemon_data = response.json()
        return pokemon_data
    else:
        print(f"Failed to retrieve data {response.status_code}")


def new_pokemon():
    global current_pokemon, current_gen_range

    pokemon_id = random.randint(current_gen_range[0], current_gen_range[1])
    current_pokemon = get_pokemon_info(pokemon_id)
    sprite_url = current_pokemon["sprites"]["front_default"]

    img_response = requests.get(sprite_url)
    img = Image.open(BytesIO(img_response.content))
    img_resized = img.resize((500, 500))

    final_sprite = ImageTk.PhotoImage(img_resized)

    img_label.configure(image=final_sprite, bg="gray20")
    img_label.image = final_sprite


def check_answer():
    global current_pokemon
    global player_score
    global attempts

    user_input = entry_box.get().lower().strip()
    correct_answer = current_pokemon["name"].lower().split("-")[0]
    if user_input == correct_answer:
        print("CORRECT!")
        player_score += 100
        new_pokemon()
        attempts = 0
        score_label.configure(fg="#4CAF50")
    else:
        print("WRONG")
        player_score -= 100
        attempts += 1
        score_label.configure(fg="#f44336")
        print(f"Attempts: {attempts}")
        if attempts >= 3:
            print("Too many incorrect guesses")
            new_pokemon()
            attempts = 0
    entry_box.delete(0, tk.END)
    score_label.configure(text=f"Score: {player_score}")


def score_reset():
    global player_score
    player_score = 0
    score_label.configure(text=f"Score: {player_score}")
    new_pokemon()


def on_gen_change(event):
    global current_gen_range
    selected = gen_var.get()
    current_gen_range = generation_ranges[selected]
    print(
        f"Changed to {selected}: Pokémon #{current_gen_range[0]}-{current_gen_range[1]}"
    )
    new_pokemon()


gen_dropdown.bind("<<ComboboxSelected>>", on_gen_change)

entry_box = tk.Entry(
    root,
    font=("Arial", 16),
    width=20,
    justify="center",
    bg="#3d3d3d",
    fg="white",
    insertbackground="white",  # Cursor color
    relief=tk.FLAT,
    borderwidth=2,
)
entry_box.pack(pady=10)
entry_box.bind("<Return>", lambda event: check_answer())

submit_button = tk.Button(
    root,
    text="Submit Answer",
    font=("Arial", 14, "bold"),
    bg="#4CAF50",  # Green
    fg="white",
    activebackground="#45a049",
    activeforeground="white",
    relief=tk.FLAT,
    padx=30,
    pady=12,
    cursor="hand2",
    command=check_answer,
)
submit_button.pack(pady=10)

reset_button.configure(command=score_reset)
sv_ttk.set_theme("dark")
new_pokemon()
root.mainloop()
