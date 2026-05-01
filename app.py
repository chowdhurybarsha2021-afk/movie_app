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

# 🔥 keep more data (IMPORTANT)
top_movies = data['title'].value_counts().head(500).index
movies = movies[movies['title'].isin(top_movies)]

movies['title'] = movies['title'].fillna('')
movie_titles = list(set(movies['title'].tolist()))

print("Data loaded successfully!")

# 🎬 TMDB API
API_KEY = "716cd4cf50388a386342607172a33377"


# 🎥 POSTER FUNCTION
def get_poster(movie_name):
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": API_KEY,
            "query": movie_name
        }

        res = requests.get(url, params=params, timeout=4)
        data = res.json()

        results = data.get("results", [])

        for m in results:
            if m.get("poster_path"):
                return "https://image.tmdb.org/t/p/w500" + m["poster_path"]

    except:
        pass

    return "https://via.placeholder.com/300x450?text=No+Image"


# 🤖 RECOMMENDATION (MULTI POSTER FIX)
def recommend(movie_name):
    movie_name = movie_name.lower().strip()

    results_list = []

    count = 0

    # 🔥 find multiple matches properly
    for title in movie_titles:
        if movie_name in title.lower():
            results_list.append({
                "title": title,
                "poster": get_poster(title)
            })
            count += 1

        if count == 6:   # 👈 LIMIT 6 posters
            break

    if not results_list:
        return [{"title": "No match found", "poster": None}]

    return results_list


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
if __name