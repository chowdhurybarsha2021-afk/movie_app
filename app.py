from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

print("Loading data...")

movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")

data = pd.merge(ratings, movies, on='movieId')

user_movie_matrix = data.pivot_table(index='userId', columns='title', values='rating')

movie_similarity = user_movie_matrix.corr()

print("Data loaded successfully!")

def recommend(movie_name):
    if movie_name in movie_similarity.columns:
        similar_movies = movie_similarity[movie_name].sort_values(ascending=False)
        similar_movies = similar_movies.drop(movie_name, errors='ignore')
        return similar_movies.head(10).index.tolist()
    return None


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


# ✅ IMPORTANT: Render compatible run
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)