import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "adopt-a-pet-secret"


# ---------------------------
# DATA (in-memory pets)
# ---------------------------
pets = [
    {"id": 1, "name": "Buddy", "species": "Dog", "age": 3,
     "description": "Friendly golden retriever who loves outdoor adventures.",
     "photo": "buddy.png", "energy": "active", "space": "big"},

    {"id": 2, "name": "Whiskers", "species": "Cat", "age": 5,
     "description": "Calm indoor cat who enjoys quiet evenings.",
     "photo": "whiskers.png", "energy": "calm", "space": "small"},

    {"id": 3, "name": "Hoppy", "species": "Rabbit", "age": 1,
     "description": "Curious rabbit who loves to explore and play.",
     "photo": "hoppy.png", "energy": "calm", "space": "small"},
]


success_stories = [
    {
        "name": "Max",
        "species": "Dog",
        "adopted_by": "The Johnson Family",
        "story": "Max was shy when he first arrived, but now he loves hiking every weekend!",
        "photo": "max.png"
    },
    {
        "name": "Luna",
        "species": "Cat",
        "adopted_by": "Sarah T.",
        "story": "Luna became Sarah's comfort companion and changed her life.",
        "photo": "luna.png"
    },
    {
        "name": "Clover",
        "species": "Rabbit",
        "adopted_by": "The Nguyen Family",
        "story": "Clover is playful and now part of the family.",
        "photo": "clover.png"
    },
]


# ---------------------------
# DATABASE SETUP
# ---------------------------
def init_db():
    conn = sqlite3.connect("adoption.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS adoption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER,
            name TEXT,
            email TEXT,
            message TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------
# ROUTES
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/pets")
def pet_list():
    species_filter = request.args.get("species", "")
    search = request.args.get("search", "").lower()

    filtered = pets

    if species_filter:
        filtered = [p for p in filtered if p["species"] == species_filter]

    if search:
        filtered = [p for p in filtered if search in p["name"].lower()]

    favourites = session.get("favourites", [])

    return render_template(
        "pets.html",
        pets=filtered,
        species_filter=species_filter,
        search=search,
        favourites=favourites
    )


@app.route("/pets/<int:pet_id>")
def pet_detail(pet_id):
    pet = next((p for p in pets if p["id"] == pet_id), None)
    return render_template("pet_detail.html", pet=pet)


# ---------------------------
# ADOPTION FORM + SAVE TO DB
# ---------------------------
@app.route("/pets/<int:pet_id>/adopt", methods=["GET", "POST"])
def adopt(pet_id):
    pet = next((p for p in pets if p["id"] == pet_id), None)

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        conn = sqlite3.connect("adoption.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO adoption (pet_id, name, email, message)
            VALUES (?, ?, ?, ?)
        """, (pet_id, name, email, message))

        conn.commit()
        conn.close()

        return render_template("adopt_success.html", pet=pet, name=name)

    return render_template("adopt_form.html", pet=pet)


# ---------------------------
# FAVORITES (SESSION)
# ---------------------------
@app.route("/favourite/<int:pet_id>")
def favourite(pet_id):
    if "favourites" not in session:
        session["favourites"] = []

    favs = list(session["favourites"])

    if pet_id in favs:
        favs.remove(pet_id)
    else:
        favs.append(pet_id)

    session["favourites"] = favs

    return redirect("/pets")


@app.route("/favourites")
def favourites():
    fav_ids = session.get("favourites", [])
    fav_pets = [p for p in pets if p["id"] in fav_ids]
    return render_template("favourites.html", pets=fav_pets)


# ---------------------------
# QUIZ
# ---------------------------
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


@app.route("/quiz/result", methods=["POST"])
def quiz_result():
    energy = request.form.get("energy")
    space = request.form.get("space")

    match = next((p for p in pets if p["energy"] == energy and p["space"] == space), pets[0])

    return render_template("quiz_result.html", pet=match)


# ---------------------------
# SUCCESS STORIES
# ---------------------------
@app.route("/stories")
def stories_page():
    return render_template("stories.html", success_stories=success_stories)


# ---------------------------
# VIEW DATABASE RECORDS
# ---------------------------
@app.route("/records")
def records():
    conn = sqlite3.connect("adoption.db")
    cursor = conn.cursor()

    cursor.execute("SELECT pet_id, name, email, message FROM adoption")
    data = cursor.fetchall()

    conn.close()

    return {
        "applications": [
            {
                "pet_id": d[0],
                "name": d[1],
                "email": d[2],
                "message": d[3]
            }
            for d in data
        ]
    }


# ---------------------------
# START APP
# ---------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)