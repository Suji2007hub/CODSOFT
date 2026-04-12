
# CineMatch – Hybrid Movie Recommendation System

**Author:** [Your Name]  
**Date:** April 2026  
**Internship Task:** 4 – Recommendation System (Content + Collaborative Filtering)

---

## 📌 Overview

CineMatch is a **hybrid movie recommendation system** that suggests movies based on user preferences using:

- Content-based filtering (TF-IDF + cosine similarity)
- Collaborative-style signals (user ratings influence)
- Genre matching
- IMDb rating normalization

It provides a clean web interface where users can select preferences, rate movies, and get personalized recommendations in real time.

---

## 🎯 Features

- 🎬 **Movie recommendations based on preferences**
- 🧠 **Hybrid scoring system**
  - Content similarity (TF-IDF + cosine similarity)
  - User rating influence
  - Genre overlap scoring
  - IMDb normalization
- ⭐ **User rating system**
  - Interactive star rating UI
  - Stored using browser localStorage
- 🔥 **Trending movies section**
  - Shows top-rated movies by IMDb score
- 🎲 **Surprise me feature**
  - Random high-quality recommendation
- 🎯 **Personalized recommendations**
  - Uses past ratings to improve suggestions
- 🌐 **Flask web interface**
  - Clean, responsive UI with JavaScript interactivity

---

## 🛠️ Tech Stack

| Component         | Technology |
|------------------|------------|
| Backend          | Python 3.8+ |
| Web Framework    | Flask |
| Data Processing  | Pandas, NumPy |
| ML/NLP           | Scikit-learn (TF-IDF, Cosine Similarity) |
| Frontend         | HTML, CSS, JavaScript |
| Storage          | Browser localStorage |

---

## 📁 Project Structure

```

task4/
│
├── app.py              # Flask backend (API + routing)
├── recommender.py      # Recommendation engine (core logic)
├── data/
│   └── movies.csv      # Dataset (50 movies)
│
├── templates/
│   └── index.html      # Frontend UI
│
├── static/
│   ├── style.css       # Styling
│   └── script.js       # Frontend logic
│
└── README.md           # Documentation

````

---

## ⚙️ Installation & Run

### 1. Install dependencies
```bash
pip install flask pandas scikit-learn numpy
````

### 2. Run the application

```bash
python app.py
```

### 3. Open in browser

```
http://127.0.0.1:5000
```

---

## 🧠 How It Works

1. **Dataset Loading**

   * Movies are loaded from CSV (title, genres, overview, rating)

2. **Text Processing**

   * Genres + overview are combined into a single text field

3. **Feature Extraction**

   * TF-IDF converts text into numerical vectors

4. **Similarity Calculation**

   * Cosine similarity finds movies similar to a selected movie

5. **Hybrid Scoring**
   Final score is calculated using:

   ```
   final_score =
       0.50 × content_similarity +
       0.30 × user_rating_signal +
       0.15 × genre_match +
       0.05 × imdb_normalized
   ```

6. **Filtering**

   * Removes already liked/rated movies
   * Applies minimum IMDb filter

7. **Output**

   * Top N recommended movies are displayed

---

## ✨ Unique Design Highlights

* ✔ Hybrid recommendation system (not just content-based)
* ✔ User rating influence improves personalization
* ✔ Genre-based filtering adds control
* ✔ IMDb normalization improves fairness
* ✔ Interactive star rating system (frontend)
* ✔ LocalStorage persistence (no database needed)
* ✔ Trending + Surprise features added
* ✔ Fully responsive UI

---

## 🧪 Evaluation Checklist

| Requirement                       | Status |
| --------------------------------- | ------ |
| Recommendation system implemented | ✅      |
| Content-based filtering           | ✅      |
| Collaborative-style signal        | ✅      |
| User preference handling          | ✅      |
| Web interface (Flask)             | ✅      |
| Clean modular structure           | ✅      |
| Personalized recommendations      | ✅      |
| Unique enhancements               | ✅      |

---

## 👨‍💻 Author & Submission

This project was completed as **Task 4** of the **CodeSoft Internship Program**.  
All code is original and written by me, **V S Sujithraa**.


---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details
