const state = {
    selectedGenres: new Set(),
    minImdb: 6.0,
    topN: 8,
    ratings: {},
};

function loadRatings() {
    const raw = localStorage.getItem("cineSuggestRatings");
    if (!raw) {
        return;
    }
    try {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === "object") {
            state.ratings = parsed;
        }
    } catch {
        state.ratings = {};
    }
}

function saveRatings() {
    localStorage.setItem("cineSuggestRatings", JSON.stringify(state.ratings));
    renderRatingsList();
}

function starHtml(current) {
    return [1, 2, 3, 4, 5]
        .map((n) => `<span class="star ${n <= current ? "active" : ""}" data-value="${n}">&#9733;</span>`)
        .join("");
}

function renderRatingsList() {
    const ratingsList = document.getElementById("ratingsList");
    const entries = Object.entries(state.ratings);

    if (entries.length === 0) {
        ratingsList.innerHTML = '<p class="muted">No ratings yet.</p>';
        return;
    }

    ratingsList.innerHTML = entries
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(
            ([title, value]) => `
                <div class="rating-item">
                    <span class="rating-title" title="${title}">${title}</span>
                    <div class="stars" data-title="${title}">${starHtml(Number(value))}</div>
                </div>
            `
        )
        .join("");

    bindStarEvents();
}

function bindStarEvents() {
    document.querySelectorAll(".stars").forEach((container) => {
        const title = container.dataset.title;
        container.querySelectorAll(".star").forEach((star) => {
            star.addEventListener("click", () => {
                state.ratings[title] = Number(star.dataset.value);
                saveRatings();
                refreshResultStars(title);
            });
        });
    });
}

function refreshResultStars(title) {
    document.querySelectorAll(".movie-rating-stars").forEach((container) => {
        if (container.dataset.title !== title) {
            return;
        }
        const current = Number(state.ratings[title] || 0);
        container.innerHTML = starHtml(current);
    });
    bindResultStars();
}

function bindResultStars() {
    document.querySelectorAll(".movie-rating-stars").forEach((container) => {
        const title = container.dataset.title;
        container.querySelectorAll(".star").forEach((star) => {
            star.addEventListener("click", () => {
                state.ratings[title] = Number(star.dataset.value);
                saveRatings();
                refreshResultStars(title);
            });
        });
    });
}

async function postJson(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
}

function movieCard(movie) {
    const genres = String(movie.genres)
        .split("|")
        .map((g) => `<span class="badge">${g}</span>`)
        .join(" ");
    const rating = Number(state.ratings[movie.title] || 0);

    return `
        <article class="card">
            <h3>${movie.title}</h3>
            <p>${genres}</p>
            <p class="muted">IMDB ${movie.imdb_rating}</p>
            <p>${movie.overview}</p>
            <div class="stars movie-rating-stars" data-title="${movie.title}">${starHtml(rating)}</div>
        </article>
    `;
}

function showResults(movies, statusMessage) {
    const statusText = document.getElementById("statusText");
    const results = document.getElementById("results");

    if (!movies || movies.length === 0) {
        statusText.textContent = "No matches found. Try fewer filters.";
        results.innerHTML = "";
        return;
    }

    statusText.textContent = statusMessage;
    results.innerHTML = movies.map(movieCard).join("");
    bindResultStars();
}

async function getRecommendations(likedTitle = "") {
    try {
        const data = await postJson("/recommend", {
            liked_title: likedTitle || document.getElementById("likedTitle").value,
            genres: Array.from(state.selectedGenres),
            min_imdb: state.minImdb,
            top_n: state.topN,
            ratings: state.ratings,
        });

        const message = likedTitle
            ? `Showing movies similar to ${likedTitle}`
            : `Showing ${data.length} recommendations`;

        showResults(data, message);
    } catch {
        document.getElementById("statusText").textContent = "Something went wrong. Please try again.";
    }
}

async function surpriseMe() {
    try {
        const movie = await postJson("/surprise", {
            genres: Array.from(state.selectedGenres),
            min_imdb: state.minImdb,
        });
        showResults([movie], "Here is your surprise pick");
    } catch {
        document.getElementById("statusText").textContent = "Could not fetch surprise movie.";
    }
}

function setupControls() {
    document.querySelectorAll(".genre-btn").forEach((button) => {
        button.addEventListener("click", () => {
            const genre = button.dataset.genre;
            if (state.selectedGenres.has(genre)) {
                state.selectedGenres.delete(genre);
                button.classList.remove("active");
            } else {
                state.selectedGenres.add(genre);
                button.classList.add("active");
            }
        });
    });

    const imdbSlider = document.getElementById("imdbSlider");
    const imdbValue = document.getElementById("imdbValue");
    imdbSlider.addEventListener("input", () => {
        state.minImdb = Number(imdbSlider.value);
        imdbValue.textContent = state.minImdb.toFixed(1);
    });

    document.getElementById("topN").addEventListener("change", (event) => {
        state.topN = Number(event.target.value);
    });

    document.getElementById("recommendBtn").addEventListener("click", () => getRecommendations());
    document.getElementById("surpriseBtn").addEventListener("click", surpriseMe);
    document.getElementById("personalizedBtn").addEventListener("click", () => getRecommendations());

    document.querySelectorAll(".trending-card").forEach((card) => {
        card.addEventListener("click", () => getRecommendations(card.dataset.title));
    });
}

function init() {
    loadRatings();
    renderRatingsList();
    setupControls();
}

init();
