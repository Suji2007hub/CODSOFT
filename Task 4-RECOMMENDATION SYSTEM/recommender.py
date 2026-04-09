import random

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RecommendationEngine:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)

        required_columns = {"title", "genres", "overview", "imdb_rating"}
        missing = required_columns - set(self.df.columns)
        if missing:
            raise ValueError(f"Dataset missing columns: {sorted(missing)}")

        self.df["genres"] = self.df["genres"].fillna("")
        self.df["overview"] = self.df["overview"].fillna("")
        self.df["imdb_rating"] = self.df["imdb_rating"].fillna(0).astype(float)
        self.df["combined_text"] = self.df["genres"] + " " + self.df["overview"]

        tfidf = TfidfVectorizer(stop_words="english")
        matrix = tfidf.fit_transform(self.df["combined_text"])
        self.similarity = cosine_similarity(matrix, matrix)
        self.title_to_idx = pd.Series(self.df.index, index=self.df["title"]).drop_duplicates()

        min_rating = self.df["imdb_rating"].min()
        max_rating = self.df["imdb_rating"].max()
        if max_rating == min_rating:
            self.df["imdb_norm"] = 0.0
        else:
            self.df["imdb_norm"] = (self.df["imdb_rating"] - min_rating) / (max_rating - min_rating)

    def get_all_titles(self) -> list[str]:
        return sorted(self.df["title"].tolist())

    def get_all_genres(self) -> list[str]:
        genres = set()
        for value in self.df["genres"]:
            for genre in value.split("|"):
                if genre:
                    genres.add(genre)
        return sorted(genres)

    def get_trending(self, n: int = 6) -> list[dict]:
        rows = self.df.sort_values("imdb_rating", ascending=False).head(max(1, n))
        return rows[["title", "genres", "overview", "imdb_rating"]].to_dict("records")

    def _genre_overlap(self, movie_genres: str, selected_genres: list[str]) -> float:
        if not selected_genres:
            return 0.0
        movie_set = set(movie_genres.split("|"))
        overlap = sum(1 for genre in selected_genres if genre in movie_set)
        return overlap / len(selected_genres)

    def recommend(
        self,
        liked_title: str,
        selected_genres: list[str],
        min_imdb: float,
        top_n: int,
        user_ratings: dict,
    ) -> list[dict]:
        top_n = max(1, min(int(top_n), 20))
        selected_genres = [g for g in selected_genres if g]

        scored = self.df.copy()
        scored["content_score"] = 0.0
        scored["rating_signal"] = 0.0

        if liked_title and liked_title in self.title_to_idx:
            liked_idx = int(self.title_to_idx[liked_title])
            scored["content_score"] = self.similarity[liked_idx]

        if user_ratings:
            for title, rating in user_ratings.items():
                if title in self.title_to_idx:
                    idx = int(self.title_to_idx[title])
                    weight = max(0.0, min(float(rating), 5.0)) / 5.0
                    scored["rating_signal"] += self.similarity[idx] * weight

        scored["genre_score"] = scored["genres"].apply(lambda value: self._genre_overlap(value, selected_genres))

        scored["final_score"] = (
            0.50 * scored["content_score"]
            + 0.30 * scored["rating_signal"]
            + 0.15 * scored["genre_score"]
            + 0.05 * scored["imdb_norm"]
        )

        if selected_genres:
            scored = scored[scored["genre_score"] > 0]

        scored = scored[scored["imdb_rating"] >= float(min_imdb)]

        exclude_titles = set()
        if liked_title:
            exclude_titles.add(liked_title)
        exclude_titles.update(user_ratings.keys())
        if exclude_titles:
            scored = scored[~scored["title"].isin(exclude_titles)]

        if scored.empty:
            return []

        rows = scored.sort_values(["final_score", "imdb_rating"], ascending=False).head(top_n)
        return rows[["title", "genres", "overview", "imdb_rating"]].to_dict("records")

    def surprise(self, min_imdb: float, selected_genres: list[str]) -> dict:
        pool = self.df[self.df["imdb_rating"] >= float(min_imdb)]

        if selected_genres:
            selected = set(selected_genres)
            pool = pool[pool["genres"].apply(lambda g: bool(selected.intersection(set(g.split("|")))))]

        if pool.empty:
            pool = self.df

        row = pool.iloc[random.randint(0, len(pool) - 1)]
        return {
            "title": row["title"],
            "genres": row["genres"],
            "overview": row["overview"],
            "imdb_rating": float(row["imdb_rating"]),
        }
