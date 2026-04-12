# recsys_app.py - Modern Dashboard Edition
# ============================================================
# Hybrid Movie Recommender – Sleek UI + Content/Collaborative
# Author: [Your Name]
# ============================================================

import os
import random
import pandas as pd
import numpy as np
from flask import Flask, render_template_string, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------- Recommender Engine (same logic, cleaned) ----------------------
class HybridRecommender:
    def __init__(self, csv_data):
        from io import StringIO
        self.df = pd.read_csv(StringIO(csv_data))
        self.df['genres'] = self.df['genres'].fillna('')
        self.df['overview'] = self.df['overview'].fillna('')
        self.df['imdb_rating'] = self.df['imdb_rating'].fillna(0).astype(float)
        self.df['text'] = self.df['genres'] + ' ' + self.df['overview']
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.df['text'])
        self.similarity = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        self.title_to_idx = pd.Series(self.df.index, index=self.df['title']).drop_duplicates()
        min_r, max_r = self.df['imdb_rating'].min(), self.df['imdb_rating'].max()
        self.df['imdb_norm'] = 0.0 if max_r == min_r else (self.df['imdb_rating'] - min_r) / (max_r - min_r)
    
    def get_all_titles(self):
        return sorted(self.df['title'].tolist())
    
    def get_all_genres(self):
        genres = set()
        for val in self.df['genres']:
            for g in val.split('|'):
                if g: genres.add(g)
        return sorted(genres)
    
    def get_trending(self, n=6):
        return self.df.nlargest(n, 'imdb_rating')[['title', 'genres', 'overview', 'imdb_rating']].to_dict('records')
    
    def _genre_overlap(self, movie_genres, selected):
        if not selected: return 0.0
        movie_set = set(movie_genres.split('|'))
        overlap = sum(1 for g in selected if g in movie_set)
        return overlap / len(selected)
    
    def recommend(self, liked_title, selected_genres, min_imdb, top_n, user_ratings):
        top_n = max(1, min(top_n, 20))
        selected_genres = [g for g in selected_genres if g]
        scored = self.df.copy()
        scored['content_score'] = 0.0
        scored['collab_score'] = 0.0
        
        if liked_title and liked_title in self.title_to_idx:
            idx = self.title_to_idx[liked_title]
            scored['content_score'] = self.similarity[idx]
        
        if user_ratings:
            for title, rating in user_ratings.items():
                if title in self.title_to_idx:
                    idx = self.title_to_idx[title]
                    weight = max(0.0, min(float(rating), 5.0)) / 5.0
                    scored['collab_score'] += self.similarity[idx] * weight
        
        scored['genre_score'] = scored['genres'].apply(lambda g: self._genre_overlap(g, selected_genres))
        scored['final_score'] = (0.45 * scored['content_score'] +
                                 0.30 * scored['collab_score'] +
                                 0.15 * scored['genre_score'] +
                                 0.10 * scored['imdb_norm'])
        
        if selected_genres:
            scored = scored[scored['genre_score'] > 0]
        scored = scored[scored['imdb_rating'] >= min_imdb]
        exclude = set()
        if liked_title: exclude.add(liked_title)
        exclude.update(user_ratings.keys())
        if exclude: scored = scored[~scored['title'].isin(exclude)]
        if scored.empty: return []
        return scored.nlargest(top_n, 'final_score')[['title', 'genres', 'overview', 'imdb_rating']].to_dict('records')
    
    def surprise_pick(self, min_imdb, selected_genres):
        pool = self.df[self.df['imdb_rating'] >= min_imdb]
        if selected_genres:
            selected_set = set(selected_genres)
            pool = pool[pool['genres'].apply(lambda g: bool(selected_set.intersection(set(g.split('|')))))]
        if pool.empty: pool = self.df
        row = pool.sample(1).iloc[0]
        return {'title': row['title'], 'genres': row['genres'], 'overview': row['overview'], 'imdb_rating': float(row['imdb_rating'])}

# ---------------------- Dataset (embedded) ----------------------
MOVIES_CSV = """movie_id,title,genres,overview,imdb_rating
1,The Shawshank Redemption,Drama,Two imprisoned men bond over years while finding hope and redemption,9.3
2,The Godfather,Crime|Drama,A mafia family struggles with loyalty legacy and power,9.2
3,The Dark Knight,Action|Crime|Drama,Batman faces the Joker in a battle for Gotham's soul,9.0
4,Inception,Action|Sci-Fi|Thriller,A thief enters dreams to steal and plant ideas,8.8
5,Forrest Gump,Comedy|Drama|Romance,A kind man witnesses and influences major moments in history,8.8
6,The Matrix,Action|Sci-Fi,A hacker discovers reality is a simulation and fights back,8.7
7,Interstellar,Adventure|Drama|Sci-Fi,Explorers travel through a wormhole to save humanity,8.6
8,The Lord of the Rings The Return of the King,Action|Adventure|Drama,Allies march to distract evil while two hobbits approach Mount Doom,8.9
9,Pulp Fiction,Crime|Drama,Interconnected stories of crime and consequence unfold in Los Angeles,8.9
10,Fight Club,Drama,An office worker forms an underground fight club with a rebel,8.8
11,Goodfellas,Biography|Crime|Drama,The rise and fall of a mob associate across decades,8.7
12,The Social Network,Biography|Drama,A student builds a social media giant and faces legal battles,7.8
13,Gladiator,Action|Adventure|Drama,A betrayed Roman general seeks justice in the arena,8.5
14,Whiplash,Drama|Music,A young drummer faces an intense and demanding instructor,8.5
15,The Grand Budapest Hotel,Adventure|Comedy|Drama,A hotel concierge and lobby boy become part of a grand adventure,8.1
16,Parasite,Comedy|Drama|Thriller,Two families from different classes become dangerously entangled,8.6
17,Joker,Crime|Drama|Thriller,A struggling comedian descends into chaos in Gotham,8.4
18,Avengers Endgame,Action|Adventure|Sci-Fi,Heroes unite for one final mission to reverse catastrophe,8.4
19,Spider-Man Into the Spider-Verse,Action|Animation|Comedy,A teen hero teams up with Spider-people from other worlds,8.4
20,The Wolf of Wall Street,Biography|Comedy|Crime,A stockbroker climbs fast and falls hard amid fraud and excess,8.2
21,The Silence of the Lambs,Crime|Drama|Thriller,An FBI trainee seeks help from a brilliant imprisoned killer,8.6
22,Back to the Future,Adventure|Comedy|Sci-Fi,A teenager travels to the past and risks his own future,8.5
23,The Lion King,Animation|Adventure|Drama,A young lion prince must reclaim his kingdom,8.5
24,The Departed,Crime|Drama|Thriller,An undercover cop and a mole race to expose each other,8.5
25,La La Land,Comedy|Drama|Music,Two artists fall in love while chasing ambitious careers,8.0
26,The Prestige,Drama|Mystery|Sci-Fi,Two rival magicians obsess over the ultimate illusion,8.5
27,The Intouchables,Biography|Comedy|Drama,An unlikely friendship changes two very different lives,8.5
28,The Green Mile,Fantasy|Drama,Guards on death row encounter a prisoner with a mysterious gift,8.6
29,Life Is Beautiful,Comedy|Drama|Romance,A father uses humor to protect his son during wartime horror,8.6
30,The Usual Suspects,Crime|Mystery|Thriller,A survivor recounts a complicated and deceptive crime story,8.5
31,Se7en,Crime|Drama|Mystery,Detectives hunt a killer inspired by the seven deadly sins,8.6
32,A Quiet Place,Horror|Mystery|Thriller,A family must remain silent to survive deadly creatures,7.5
33,John Wick,Action|Crime|Thriller,A retired hitman returns after a brutal personal loss,7.4
34,Coco,Animation|Adventure|Family,A boy enters the land of the dead to uncover family truths,8.4
35,Your Name,Animation|Drama|Fantasy,Two teenagers mysteriously swap bodies across distance and time,8.4
36,The Truman Show,Comedy|Drama,A man discovers his whole life is a television show,8.1
37,The Pianist,Biography|Drama|Music,A musician fights to survive in war-torn Europe,8.5
38,The Shining,Horror|Drama,Isolation and fear slowly consume a family in a remote hotel,8.4
39,The Dark Knight Rises,Action|Drama,Bruce Wayne returns to face a ruthless new enemy,8.4
40,The Lego Movie,Animation|Adventure|Comedy,An ordinary builder is mistaken for a special hero,7.7
41,Mad Max Fury Road,Action|Adventure|Sci-Fi,Rebels flee a tyrant across a brutal desert wasteland,8.1
42,The Sixth Sense,Horror|Mystery|Thriller,A boy who sees spirits seeks help from a troubled doctor,8.1
43,The Incredibles,Action|Animation|Family,A superhero family comes out of retirement to save the world,8.0
44,Good Will Hunting,Drama|Romance,A gifted janitor learns to confront his past and potential,8.3
45,The Breakfast Club,Comedy|Drama,Five students discover unexpected common ground in detention,7.8
46,Die Hard,Action|Thriller,A cop battles terrorists inside a skyscraper,8.2
47,The Big Lebowski,Comedy|Crime,A laid-back bowler is dragged into a bizarre crime plot,8.1
48,The Notebook,Romance|Drama,A couple's love story survives class conflict and time,7.8
49,Shutter Island,Mystery|Thriller,A marshal investigates a disappearance at an isolated asylum,8.2
50,The Help,Drama,A writer exposes injustice faced by maids in the deep south,8.1
"""

# ---------------------- Flask App with Modern Dashboard ----------------------
app = Flask(__name__)
recommender = HybridRecommender(MOVIES_CSV)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CineMatch | AI Recommender</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            transition: background 0.3s, color 0.3s;
        }
        body.light {
            background: #f8fafc;
            color: #0f172a;
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #334155; border-radius: 10px; }
        ::-webkit-scrollbar-thumb { background: #f59e0b; border-radius: 10px; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        /* Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 15px;
        }
        .logo h1 {
            font-size: 1.8rem;
            background: linear-gradient(135deg, #f59e0b, #ef4444);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .logo p { font-size: 0.85rem; opacity: 0.7; }
        .theme-toggle {
            background: #334155;
            border: none;
            padding: 10px 16px;
            border-radius: 40px;
            cursor: pointer;
            font-weight: 500;
            transition: 0.2s;
            color: white;
        }
        body.light .theme-toggle { background: #e2e8f0; color: #0f172a; }
        /* Grid layout */
        .dashboard {
            display: grid;
            grid-template-columns: 320px 1fr 300px;
            gap: 24px;
        }
        @media (max-width: 1100px) {
            .dashboard { grid-template-columns: 1fr; }
        }
        /* Cards */
        .card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 28px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.2s;
        }
        body.light .card {
            background: white;
            border: 1px solid #e2e8f0;
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
        }
        .card h2 { font-size: 1.3rem; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
        /* Form elements */
        select, input[type="range"] {
            width: 100%;
            padding: 10px 14px;
            border-radius: 40px;
            border: 1px solid #475569;
            background: #1e293b;
            color: #f1f5f9;
            margin-bottom: 16px;
            font-size: 0.9rem;
        }
        body.light select, body.light input[type="range"] {
            background: white;
            border-color: #cbd5e1;
            color: #0f172a;
        }
        .genre-btns {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }
        .genre-btn {
            background: #334155;
            border: none;
            padding: 6px 14px;
            border-radius: 40px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: 0.1s;
            color: #f1f5f9;
        }
        body.light .genre-btn { background: #e2e8f0; color: #0f172a; }
        .genre-btn.active { background: #f59e0b; color: white; }
        button {
            background: #f59e0b;
            border: none;
            padding: 10px 18px;
            border-radius: 40px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.2s;
            color: white;
        }
        button:hover { transform: scale(1.02); background: #d97706; }
        .btn-secondary { background: #475569; }
        /* Movie grid */
        .movie-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }
        .movie-card {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 20px;
            padding: 14px;
            transition: 0.2s;
            border: 1px solid #334155;
        }
        body.light .movie-card { background: #fef9e8; border-color: #e2e8f0; }
        .movie-card:hover { transform: translateY(-4px); border-color: #f59e0b; }
        .movie-card h3 { font-size: 1rem; margin-bottom: 6px; }
        .badge {
            display: inline-block;
            background: #f59e0b20;
            color: #f59e0b;
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 0.7rem;
            margin: 4px 4px 0 0;
        }
        .stars {
            display: flex;
            gap: 4px;
            margin-top: 10px;
        }
        .star {
            font-size: 18px;
            cursor: pointer;
            color: #64748b;
            transition: 0.1s;
        }
        .star.active { color: #f5c518; }
        .star:hover { transform: scale(1.1); }
        .trending-item {
            cursor: pointer;
            padding: 10px;
            border-radius: 16px;
            transition: 0.1s;
        }
        .trending-item:hover { background: #334155; }
        body.light .trending-item:hover { background: #f1f5f9; }
        .skeleton {
            background: linear-gradient(90deg, #334155 25%, #475569 50%, #334155 75%);
            background-size: 200% 100%;
            animation: shimmer 1.2s infinite;
            border-radius: 16px;
            height: 180px;
        }
        @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #f59e0b;
            color: #0f172a;
            padding: 12px 20px;
            border-radius: 40px;
            font-weight: 500;
            z-index: 1000;
            animation: fadeOut 2s forwards;
        }
        @keyframes fadeOut { 0% { opacity: 1; } 70% { opacity: 1; } 100% { opacity: 0; visibility: hidden; } }
        .rating-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            font-size: 0.85rem;
        }
        hr { margin: 20px 0; border-color: #334155; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">
            <h1>🎬 CineMatch</h1>
            <p>Hybrid AI Recommender · Content + Collaborative</p>
        </div>
        <button class="theme-toggle" id="themeToggle">🌙 Dark</button>
    </div>

    <div class="dashboard">
        <!-- Left Panel: Controls -->
        <div class="card">
            <h2>🎛️ Preferences</h2>
            <label>🎥 Movie you like</label>
            <select id="likedMovie">
                <option value="">-- None --</option>
                {% for m in movies %}
                <option value="{{ m }}">{{ m }}</option>
                {% endfor %}
            </select>
            <label>🏷️ Select genres</label>
            <div id="genreContainer" class="genre-btns">
                {% for g in genres %}
                <button class="genre-btn" data-genre="{{ g }}">{{ g }}</button>
                {% endfor %}
            </div>
            <label>⭐ Min IMDb: <span id="imdbVal">6.0</span></label>
            <input type="range" id="imdbSlider" min="0" max="10" step="0.5" value="6">
            <label>📊 Results count</label>
            <select id="topN">
                <option value="4">4</option>
                <option value="8" selected>8</option>
                <option value="12">12</option>
            </select>
            <div style="display: flex; gap: 10px; margin-top: 10px;">
                <button id="recommendBtn" style="flex:1;">🔍 Recommend</button>
                <button id="surpriseBtn" class="btn-secondary" style="flex:1;">🎲 Surprise</button>
            </div>
            <button id="personalizedBtn" style="width:100%; margin-top: 12px;">❤️ Personalized (use my ratings)</button>
        </div>

        <!-- Middle Panel: Results -->
        <div class="card">
            <h2>📽️ Recommendations</h2>
            <div id="resultsArea">
                <div class="skeleton" style="height: 200px;"></div>
            </div>
        </div>

        <!-- Right Panel: Trending + Ratings -->
        <div class="card">
            <h2>🔥 Trending Now</h2>
            <div id="trendingList">
                {% for m in trending %}
                <div class="trending-item" data-title="{{ m.title }}">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{{ m.title }}</strong>
                        <span class="badge">⭐ {{ m.imdb_rating }}</span>
                    </div>
                    <p style="font-size: 0.7rem; opacity: 0.7;">{{ m.overview[:80] }}...</p>
                </div>
                {% endfor %}
            </div>
            <hr>
            <h2>⭐ Your Ratings</h2>
            <div id="ratingsList">No ratings yet. Rate any movie from results.</div>
        </div>
    </div>
</div>

<script>
    // ---------- State ----------
    let selectedGenres = new Set();
    let minImdb = 6.0;
    let topN = 8;
    let userRatings = {};

    // ---------- Theme ----------
    const themeToggle = document.getElementById('themeToggle');
    if (localStorage.getItem('theme') === 'light') {
        document.body.classList.add('light');
        themeToggle.innerHTML = '☀️ Light';
    } else {
        themeToggle.innerHTML = '🌙 Dark';
    }
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('light');
        const isLight = document.body.classList.contains('light');
        localStorage.setItem('theme', isLight ? 'light' : 'dark');
        themeToggle.innerHTML = isLight ? '☀️ Light' : '🌙 Dark';
    });

    // ---------- Ratings localStorage ----------
    function loadRatings() {
        const stored = localStorage.getItem('cineMatchRatings');
        if (stored) {
            try { userRatings = JSON.parse(stored); } catch(e) {}
        }
        renderRatings();
    }
    function saveRatings() {
        localStorage.setItem('cineMatchRatings', JSON.stringify(userRatings));
        renderRatings();
        showToast('Ratings saved!');
    }
    function renderRatings() {
        const container = document.getElementById('ratingsList');
        const entries = Object.entries(userRatings);
        if (entries.length === 0) {
            container.innerHTML = '<p style="opacity:0.6;">No ratings yet. Click stars on any movie.</p>';
            return;
        }
        container.innerHTML = entries.map(([title, val]) => `
            <div class="rating-item">
                <span style="max-width: 150px; overflow: hidden; text-overflow: ellipsis;">${title}</span>
                <div class="stars" data-title="${title}">${starHtml(val)}</div>
            </div>
        `).join('');
        attachStarEvents();
    }
    function starHtml(rating) {
        let html = '';
        for (let i=1; i<=5; i++) {
            html += `<span class="star ${i<=rating ? 'active' : ''}" data-val="${i}">★</span>`;
        }
        return html;
    }
    function attachStarEvents() {
        document.querySelectorAll('.rating-item .stars').forEach(container => {
            const title = container.dataset.title;
            container.querySelectorAll('.star').forEach(star => {
                star.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const newVal = parseInt(star.dataset.val);
                    userRatings[title] = newVal;
                    saveRatings();
                    updateResultStars(title, newVal);
                });
            });
        });
    }
    function updateResultStars(title, rating) {
        const resultStars = document.querySelectorAll(`.movie-rating-stars[data-title="${title}"]`);
        resultStars.forEach(container => {
            container.innerHTML = starHtml(rating);
        });
        attachResultStarEvents();
    }
    function attachResultStarEvents() {
        document.querySelectorAll('.movie-rating-stars').forEach(container => {
            const title = container.dataset.title;
            container.querySelectorAll('.star').forEach(star => {
                star.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const newVal = parseInt(star.dataset.val);
                    userRatings[title] = newVal;
                    saveRatings();
                    updateResultStars(title, newVal);
                });
            });
        });
    }

    // ---------- UI Helpers ----------
    function showToast(msg) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerText = msg;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }

    function setLoading(show) {
        const area = document.getElementById('resultsArea');
        if (show) {
            area.innerHTML = '<div class="skeleton" style="height: 200px;"></div><div class="skeleton" style="height: 200px; margin-top:16px;"></div>';
        }
    }

    // ---------- API Calls ----------
    async function getRecommendations(likedTitle = null) {
        setLoading(true);
        const payload = {
            liked_title: likedTitle || document.getElementById('likedMovie').value,
            genres: Array.from(selectedGenres),
            min_imdb: minImdb,
            top_n: topN,
            ratings: userRatings
        };
        try {
            const res = await fetch('/recommend', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            displayResults(data);
        } catch(err) {
            showToast('Error fetching recommendations');
            setLoading(false);
        }
    }

    async function surpriseMe() {
        setLoading(true);
        const payload = {
            genres: Array.from(selectedGenres),
            min_imdb: minImdb
        };
        try {
            const res = await fetch('/surprise', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify(payload)
            });
            const movie = await res.json();
            displayResults([movie]);
        } catch(err) {
            showToast('Surprise failed');
            setLoading(false);
        }
    }

    function displayResults(movies) {
        const container = document.getElementById('resultsArea');
        if (!movies.length) {
            container.innerHTML = '<p style="opacity:0.6;">😞 No movies match your filters. Try lowering IMDb rating or selecting fewer genres.</p>';
            return;
        }
        let html = '<div class="movie-grid">';
        for (const m of movies) {
            const genres = m.genres.split('|').map(g => `<span class="badge">${g}</span>`).join('');
            const currentRating = userRatings[m.title] || 0;
            html += `
                <div class="movie-card">
                    <h3>${m.title}</h3>
                    <div>${genres}</div>
                    <div><span class="badge">⭐ ${m.imdb_rating}</span></div>
                    <p style="font-size: 0.75rem; margin-top: 8px; opacity:0.8;">${m.overview.substring(0, 100)}...</p>
                    <div class="stars movie-rating-stars" data-title="${m.title}">${starHtml(currentRating)}</div>
                </div>
            `;
        }
        html += '</div>';
        container.innerHTML = html;
        attachResultStarEvents();
        setLoading(false);
    }

    // ---------- Event Binding ----------
    function setupUI() {
        // Genre buttons
        document.querySelectorAll('.genre-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const genre = btn.dataset.genre;
                if (selectedGenres.has(genre)) {
                    selectedGenres.delete(genre);
                    btn.classList.remove('active');
                } else {
                    selectedGenres.add(genre);
                    btn.classList.add('active');
                }
            });
        });
        // IMDb slider
        const slider = document.getElementById('imdbSlider');
        const imdbSpan = document.getElementById('imdbVal');
        slider.addEventListener('input', () => {
            minImdb = parseFloat(slider.value);
            imdbSpan.innerText = minImdb.toFixed(1);
        });
        document.getElementById('topN').addEventListener('change', (e) => topN = parseInt(e.target.value));
        document.getElementById('recommendBtn').addEventListener('click', () => getRecommendations());
        document.getElementById('surpriseBtn').addEventListener('click', surpriseMe);
        document.getElementById('personalizedBtn').addEventListener('click', () => getRecommendations());
        // Trending clicks
        document.querySelectorAll('.trending-item').forEach(item => {
            item.addEventListener('click', () => getRecommendations(item.dataset.title));
        });
    }

    loadRatings();
    setupUI();
    // Initial load of trending (already rendered from server)
    setLoading(false);
</script>
</body>
</html>
"""

# ---------------------- Routes ----------------------
@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        movies=recommender.get_all_titles(),
        genres=recommender.get_all_genres(),
        trending=recommender.get_trending(6)
    )

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    results = recommender.recommend(
        liked_title=data.get('liked_title', ''),
        selected_genres=data.get('genres', []),
        min_imdb=float(data.get('min_imdb', 0)),
        top_n=int(data.get('top_n', 8)),
        user_ratings=data.get('ratings', {})
    )
    return jsonify(results)

@app.route('/surprise', methods=['POST'])
def surprise():
    data = request.json
    movie = recommender.surprise_pick(
        min_imdb=float(data.get('min_imdb', 0)),
        selected_genres=data.get('genres', [])
    )
    return jsonify(movie)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🎬 CineMatch – Modern Dashboard Edition")
    print("Open: http://localhost:5000")
    print("="*50)
    app.run(debug=True, port=5000)