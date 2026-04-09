# Task 4 - Recommendation System

This is a clean, simple movie recommendation system built for end users.

## Features
- Easy preference inputs (movie, genres, minimum IMDB, top N)
- Content-based recommendations using TF-IDF and cosine similarity
- Personalized signal from user star ratings (stored in browser local storage)
- Trending quick-pick cards for one-click similar recommendations
- Surprise movie button

## Project Files
- app.py: Flask routes and API endpoints
- recommender.py: recommendation logic
- data/movies.csv: movie dataset
- templates/index.html: dashboard UI
- static/style.css: styling
- static/script.js: interactivity

## Run
1. Install dependencies:
   pip install -r requirements.txt
2. Start server:
   python app.py
3. Open:
   http://127.0.0.1:5000
