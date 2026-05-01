from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

print("Loading data...")

movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")

# 🔥 reduce memory usage
data = pd.merge(ratings, movies, on='movieId')

top_movies = data['title'].value_counts().head(100).index
data = data[data['title'].isin(top_movies)]

user_movie_matrix = data.pivot_table(index='userId', columns='title', values='rating')
movie_similarity = user_movie_matrix.corr()

print("Data loaded successfully!")


# 🧠 SMART SEARCH (NEW)
def recommend(movie_name):
    movie_name = movie_name.lower()

    matches = [title for title in movie_similarity.columns
               if movie_name in title.lower()]

    if len(matches) > 0:
        best_match = matches[0]
        similar_movies = movie_similarity[best_match].sort_values(ascending=False)
        similar_movies = similar_movies.drop(best_match, errors='ignore')
        return similar_movies.head(10).index.tolist()

    return ["No match found"]


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


# 🚀 Render safe run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)