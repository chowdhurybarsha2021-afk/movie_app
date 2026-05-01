from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd
import os
import requests

app = Flask(__name__)
app.secret_key = "secret123"

print("Loading data...")

# =========================
# 📌 LOAD DATA (LIGHT + SAFE)
# =========================
movies = pd.read_csv("movies.csv", usecols=["movieId", "title"])
ratings = pd.read_csv("ratings.csv", usecols=["movieId"])
bollywood = pd.read_csv("bollywood_movies.csv", usecols=["movieId", "title"])

movies = pd.concat([movies, bollywood], ignore_index=True)
movies = movies.dropna(subset=["title"])

data = pd.merge(ratings, movies, on="movieId")

# 🔥 MEMORY SAFE
top_titles = data["title"].value_counts().head(60).index
movies = movies[movies["title"].isin(top_titles)]

movie_titles = list(set(movies["title"].astype(str).tolist()))

print("Data loaded successfully!")

# =========================
# 🎬 TMDB API
# =========================
API_KEY = "716cd4cf50388a386342607172a33377"
BASE_URL = "https://api.themoviedb.org/3/search/movie"
IMG_URL = "https://image.tmdb.org/t/p/w500"

# =========================
# 🎥 POSTER FUNCTION
# =========================
def get_poster(movie_name):
    try:
        clean_name = movie_name.split("(")[0].strip()

        res = requests.get(
            BASE_URL,
            params={"api_key": API_KEY, "query": clean_name},
            timeout=3
        )

        data = res.json()
        results = data.get("results", [])

        for movie in results:
            if movie.get("poster_path"):
                return IMG_URL + movie["poster_path"]

    except Exception as e:
        print("Poster error:", e)

    return "https://via.placeholder.com/300x450?text=No+Image"

# =========================
# 🤖 RECOMMENDER
# =========================
def recommend(movie_name):
    movie_name = movie_name.lower().strip()

    matches = [
        title for title in movie_titles
        if movie_name in title.lower()
    ]

    if not matches:
        return [{"title": "No match found 😢", "poster": None}]

    results = []

    for name in matches[:6]:
        results.append({
            "title": name,
            "poster": get_poster(name)
        })

    return results

# =========================
# 🔐 LOGIN SYSTEM
# =========================
users = {
    "admin": "1234",
    "user": "1234"
}

# 🔥 ROOT → ALWAYS LOGIN FIRST
@app.route("/")
def root():
    return redirect(url_for("login"))

# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

# 🔓 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# 🏠 HOME (AFTER LOGIN)
@app.route("/home", methods=["GET", "POST"])
def home():

    if "user" not in session:
        return redirect(url_for("login"))

    movie_name = ""
    recommendations = []

    if request.method == "POST":
        movie_name = request.form.get("movie")

        if movie_name:
            recommendations = recommend(movie_name)

    return render_template(
        "index.html",
        recommendations=recommendations,
        movie_name=movie_name,
        user=session.get("user")
    )

# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)