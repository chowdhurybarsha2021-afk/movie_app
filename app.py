from flask import Flask, render_template, request
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

print("Loading data...")

# 📌 Load datasets
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")
bollywood = pd.read_csv("bollywood_movies.csv")

# 📌 Merge movies (Hollywood + Bollywood)
movies = pd.concat([movies, bollywood], ignore_index=True)

# 📌 Merge ratings
data = pd.merge(ratings, movies, on='movieId')

# 🔥 Reduce memory usage
top_movies = data['title'].value_counts().head(100).index
data = data[data['title'].isin(top_movies)]

# 🧠 AI CONTENT FEATURES (REAL NLP MODEL)
movies['title'] = movies['title'].fillna('')

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['title'])

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

movie_titles = movies['title'].tolist()

print("Data loaded successfully!")


# 🤖 AI RECOMMENDATION FUNCTION
def recommend(movie_name):
    movie_name = movie_name.lower().strip()

    matches = [i for i, title in enumerate(movie_titles)
               if movie_name in title.lower() or title.lower() in movie_name]

    if not matches:
        return ["No match found"]

    idx = matches[0]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:11]

    movie_indices = [i[0] for i in sim_scores]

    return [movie_titles[i] for i in movie_indices]


# 🌐 Routes
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