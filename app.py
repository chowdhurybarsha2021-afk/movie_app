from flask import Flask, render_template, request
import pandas as pd
import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

print("Loading data...")

# 📌 Load datasets
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")
bollywood = pd.read_csv("bollywood_movies.csv")

# 📌 Merge movies
movies = pd.concat([movies, bollywood], ignore_index=True)

# 📌 Merge ratings
data = pd.merge(ratings, movies, on='movieId')

# 🔥 Reduce memory usage
top_movies = data['title'].value_counts().head(100).index
data = data[data['title'].isin(top_movies)]

# 🧠 AI FEATURES
movies['title'] = movies['title'].fillna('')

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['title'])

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

movie_titles = movies['title'].tolist()

print("Data loaded successfully!")

# 🎬 TMDB API KEY
API_KEY = "716cd4cf50388a386342607172a33377"


# 🎥 GET POSTER (DEBUG VERSION)
def get_poster(movie_name):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_name}"
    
    response = requests.get(url)
    data = response.json()

    print("API CHECK:", movie_name)  # 🔥 DEBUG

    results = data.get("results", [])

    if len(results) > 0:
        poster_path = results[0].get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path

    return None


# 🤖 AI RECOMMENDATION FUNCTION
def recommend(movie_name):
    movie_name = movie_name.lower().strip()

    matches = [
        i for i, title in enumerate(movie_titles)
        if movie_name in title.lower() or title.lower() in movie_name
    ]

    if not matches:
        return [{"title": "No match found", "poster": None}]

    idx = matches[0]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:11]

    movie_indices = [i[0] for i in sim_scores]

    results = []

    for i in movie_indices:
        name = movie_titles[i]

        poster = get_poster(name)

        results.append({
            "title": name,
            "poster": poster
        })

    return results


# 🌐 ROUTES
@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = None
    movie_name = ""

    if request.method == "POST":
        movie_name = request.form["movie"]
        recommendations = recommend(movie_name)

    return render_template("index.html",
                           recommendations=recommendations,
                           movie_name=movie_name)


# 🚀 RUN APP
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)