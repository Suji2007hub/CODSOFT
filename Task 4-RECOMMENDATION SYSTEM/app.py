from flask import Flask, jsonify, render_template, request

from recommender import RecommendationEngine


app = Flask(__name__)
engine = RecommendationEngine("data/movies.csv")


@app.route("/")
def index():
    return render_template(
        "index.html",
        movies=engine.get_all_titles(),
        genres=engine.get_all_genres(),
        trending=engine.get_trending(6),
    )


@app.route("/recommend", methods=["POST"])
def recommend():
    payload = request.get_json(silent=True) or {}
    results = engine.recommend(
        liked_title=payload.get("liked_title", ""),
        selected_genres=payload.get("genres", []),
        min_imdb=float(payload.get("min_imdb", 0.0)),
        top_n=int(payload.get("top_n", 8)),
        user_ratings=payload.get("ratings", {}),
    )
    return jsonify(results)


@app.route("/surprise", methods=["POST"])
def surprise():
    payload = request.get_json(silent=True) or {}
    return jsonify(
        engine.surprise(
            min_imdb=float(payload.get("min_imdb", 0.0)),
            selected_genres=payload.get("genres", []),
        )
    )


if __name__ == "__main__":
    app.run(debug=True)
