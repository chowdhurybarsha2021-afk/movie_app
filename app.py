from flask import Flask, render_template, request
import pandas as pd
import os
import requests

app = Flask(__name__)

print("Loading data...")

# =========================
# 📌 LOAD DATA (LIGHT + SAFE FOR RENDER)
# =========================
movies = pd.read_csv("movies.csv")[["movieId", "title"]]
ratings = pd.read_csv("ratings.csv")[["movieId"]]
bollywood = pd.read_csv("bollywood_movies.csv")[["movieId", "title"]]

movies = pd.concat([movies, bollywood], ignore_index=True)
movies = movies.dropna(subset=["title"])

data = pd.merge(ratings, movies, on="movieId")

# 🔥 LIMIT (VERY IMPORTANT FOR RENDER)
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
# 🎥 GET POSTER (SAFE)
# =========================
def get_poster(movie_name):
    try:
        clean_name = movie_name.split("(")[0].strip()

        res = requests.get(
            BASE_URL,
            params={"api_key": API_KEY, "query": clean_name},
            timeout=4
        )

        data = res.json()
        results = data.get("results", [])

        for movie in results[:3]:
            poster = movie.get("poster_path")
            if poster:
                return IMG_URL + poster

    except:
        pass

    return "https://via.placeholder.com/300x450?text=No+Image"

# =========================
# 🤖 RECOMMENDER (SIMPLE + FAST)
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
# 🌐 ROUTE
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    movie_name = ""
    recommendations = []

    if request.method == "POST":
        movie_name = request.form.get("movie")
        if movie_name:
            recommendations = recommend(movie_name)

    return render_template(
        "index.html",
        recommendations=recommendations,
        movie_name=movie_name
    )

# =========================
# 🚀 RUN (RENDER SAFE)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)