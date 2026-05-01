from flask import Flask, render_template, request
import pandas as pd
import os
import requests

app = Flask(__name__)

print("Loading data...")

# 📌 Load data (light + safe)
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")
bollywood = pd.read_csv("bollywood_movies.csv")

# merge datasets
movies = pd.concat([movies, bollywood], ignore_index=True)
data = pd.merge(ratings, movies, on='movieId')

# 🔥 LIMIT DATA (Render safe)
top_movies = data['title'].value_counts().head(50).index
movies = movies[movies['title'].isin(top_movies)]

movies['title'] = movies['title'].fillna('')
movie_titles = list(set(movies['title'].tolist()))  # remove duplicates

print("Data loaded successfully!")

# 🎬 TMDB API
API_KEY = "716cd4cf50388a386342607172a33377"


# 🎥 POSTER (ROBUST VERSION)
def get_poster(movie_name):
    try:
        clean_name = movie_name.split("(")[0].strip()

        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": API_KEY,
            "query": clean_name
        }

        res = requests.get(url, params=params, timeout=4)
        data = res.json()

        results = data.get("results", [])

        # 🔥 loop all results until valid poster found
        for movie in results:
            poster = movie.get("poster_path")
            if poster:
                return "https://image.tmdb.org/t/p/w500" + poster

    except Exception as e:
        print("Poster error:", e)

    return "https://via.placeholder.com/300x450?text=No+Image"


# 🤖 RECOMMENDATION ENGINE (IMPROVED)
def recommend(movie_name):
    movie_name = movie_name.lower().strip()

    matches = [
        title for title in movie_titles
        if movie_name in title.lower()
    ]

    if not matches:
        return [{"title": "No match found", "poster": None}]

    results = []

    # 🔥 show max 6 movies (UI clean)
    for name in matches[:6]:
        results.append({
            "title": name,
            "poster": get_poster(name)
        })

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


# 🚀 RUN (Render safe)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)