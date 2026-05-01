from flask import Flask, render_template, request
import pandas as pd
import os
import requests

app = Flask(__name__)

print("Loading data...")

# 📌 Load data
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")
bollywood = pd.read_csv("bollywood_movies.csv")

movies = pd.concat([movies, bollywood], ignore_index=True)
data = pd.merge(ratings, movies, on='movieId')

# 🔥 SAFE LIMIT (Render friendly)
data = data.sample(n=12000, random_state=42)

movies = movies.dropna(subset=['title'])
movies['title'] = movies['title'].astype(str)

movie_titles = list(set(movies['title'].tolist()))

print("Data loaded successfully!")

API_KEY = "716cd4cf50388a386342607172a33377"


# 🎥 POSTER FIX (VERY IMPORTANT)
def get_poster(movie_name):
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": API_KEY,
            "query": movie_name
        }

        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        results = data.get("results", [])

        # 🔥 loop until valid poster found
        for m in results:
            if m.get("poster_path"):
                return "https://image.tmdb.org/t/p/w500" + m["poster_path"]

    except Exception as e:
        print("Poster error:", e)

    return "https://via.placeholder.com/300x450?text=No+Image"


# 🤖 RECOMMENDATION ENGINE (FIXED MULTI OUTPUT)
def recommend(movie_name):
    movie_name = movie_name.lower().strip()

    results = []

    # 🔥 better matching (not strict)
    for title in movie_titles:
        if movie_name in title.lower():
            results.append({
                "title": title,
                "poster": get_poster(title)
            })

        if len(results) >= 6:
            break

    # fallback
    if not results:
        return [{
            "title": "No match found",
            "poster": None
        }]

    return results


# 🌐 ROUTE
@app.route("/", methods=["GET", "POST"])
def home():
    movie_name = ""
    recommendations = None

    if request.method == "POST":
        movie_name = request.form["movie"]
        recommendations = recommend(movie_name)

    return render_template(
        "index.html",
        recommendations=recommendations,
        movie_name=movie_name
    )


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)