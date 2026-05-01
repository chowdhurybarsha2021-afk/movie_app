from flask import Flask, render_template, request
import pandas as pd
import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

print("Loading data...")

# 🟢 MEMORY SAFE LOAD
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")
bollywood = pd.read_csv("bollywood_movies.csv")

movies = pd.concat([movies, bollywood], ignore_index=True)
data = pd.merge(ratings, movies, on='movieId')

# 🔥 SMALL DATA ONLY (Render safe)
top_movies = data['title'].value_counts().head(50).index
data = data[data['title'].isin(top_movies)]

movies['title'] = movies['title'].fillna('')

# 🧠 SIMPLE AI MODEL
tfidf = TfidfVectorizer(stop_words='english', max_features=2000)
tfidf_matrix = tfidf.fit_transform(movies['title'])

cosine_sim = cosine_similarity(tfidf_matrix)

movie_titles = movies['title'].tolist()

print("Data loaded successfully!")

# 🎬 TMDB API
API_KEY = "716cd4cf50388a386342607172a33377"


# 🎥 POSTER FUNCTION (FINAL FIX)
def get_poster(movie_name):
    try:
        clean_name = movie_name.split("(")[0].strip()

        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": API_KEY, "query": clean_name}

        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        results = data.get("results", [])

        if results:
            poster_path = results[0].get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path

    except:
        pass

    return "https://via.placeholder.com/300x450?text=No+Image"


# 🤖 RECOMMENDATION
def recommend(movie_name):
    movie_name = movie_name.lower().strip()

    matches = [
        i for i, title in enumerate(movie_titles)
        if movie_name in title.lower()
    ]

    if not matches:
        return [{"title": "No match found", "poster": None}]

    idx = matches[0]

    sim_scores = sorted(
        list(enumerate(cosine_sim[idx])),
        key=lambda x: x[1],
        reverse=True
    )[1:11]

    results = []

    for i, _ in sim_scores:
        name = movie_titles[i]
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

    return render_template("index.html",
                           recommendations=recommendations,
                           movie_name=movie_name)


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)