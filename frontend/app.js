const searchForm = document.querySelector('#search-form');
const queryInput = document.querySelector('#movie-query');
const searchStatus = document.querySelector('#search-status');
const movieResults = document.querySelector('#movie-results');
const recommendationSection = document.querySelector('#recommendation-section');
const selectedMovie = document.querySelector('#selected-movie');
const recommendationStatus = document.querySelector('#recommendation-status');
const recommendations = document.querySelector('#recommendations');
const limitSelect = document.querySelector('#limit');
const modelSelect = document.querySelector('#model');

loadAvailableModels();

async function loadAvailableModels() {
  try {
    const response = await fetch('/models');
    if (!response.ok) throw new Error(await errorMessage(response));
    const availableModels = await response.json();
    [...modelSelect.options].forEach((option) => {
      const isAvailable = availableModels.includes(option.value);
      option.disabled = !isAvailable;
      if (!isAvailable) option.textContent = `${option.textContent.split(' (')[0]} (not loaded)`;
    });
    if (!availableModels.includes(modelSelect.value) && availableModels.length) {
      modelSelect.value = availableModels[0];
    }
  } catch {
    modelSelect.value = 'item';
  }
}

searchForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();
  if (!query) return;

  movieResults.replaceChildren();
  setStatus(searchStatus, 'Searching the catalog...');
  try {
    const response = await fetch(`/movies?query=${encodeURIComponent(query)}&limit=10&model=${modelSelect.value}`);
    if (!response.ok) throw new Error(await errorMessage(response));
    const movies = await response.json();
    renderMovieResults(movies);
  } catch (error) {
    setStatus(searchStatus, error.message, true);
  }
});

limitSelect.addEventListener('change', () => {
  const movieId = recommendationSection.dataset.movieId;
  if (movieId) loadRecommendations(Number(movieId));
});

function renderMovieResults(movies) {
  movieResults.replaceChildren();
  if (!movies.length) {
    setStatus(searchStatus, 'No matching movies found. Try a broader title.');
    return;
  }
  setStatus(searchStatus, `${movies.length} ${movies.length === 1 ? 'match' : 'matches'} found`);
  movies.forEach((movie) => {
    const button = document.createElement('button');
    button.className = 'movie-result';
    button.type = 'button';
    button.innerHTML = `<span class="movie-result-title">${escapeHtml(movie.title)}</span><span class="movie-result-meta">${escapeHtml(movie.genres)}</span><span class="result-arrow" aria-hidden="true">&nearr;</span>`;
    button.addEventListener('click', () => loadRecommendations(movie.movieId, movie));
    movieResults.append(button);
  });
}

async function loadRecommendations(movieId, movie) {
  recommendationSection.hidden = false;
  recommendationSection.dataset.movieId = movieId;
  if (movie) {
    selectedMovie.innerHTML = `<span>Recommendations inspired by</span><strong>${escapeHtml(movie.title)}</strong><small>${escapeHtml(movie.genres)}</small>`;
  }
  recommendations.replaceChildren();
  setStatus(recommendationStatus, 'Finding similar films...');
  recommendationSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

  try {
    const response = await fetch(`/recommendations?movie_id=${movieId}&limit=${limitSelect.value}&model=${modelSelect.value}`);
    if (!response.ok) throw new Error(await errorMessage(response));
    const data = await response.json();
    renderRecommendations(data.recommendations);
  } catch (error) {
    setStatus(recommendationStatus, error.message, true);
  }
}

function renderRecommendations(items) {
  recommendations.replaceChildren();
  if (!items.length) {
    setStatus(recommendationStatus, 'No similar films were found.');
    return;
  }
  setStatus(recommendationStatus, `${items.length} recommendations`);
  items.forEach((movie, index) => {
    const article = document.createElement('article');
    article.className = 'recommendation';
    article.style.setProperty('--delay', `${index * 45}ms`);
    article.innerHTML = `<span class="recommendation-index">${String(index + 1).padStart(2, '0')}</span><div class="recommendation-copy"><h3>${escapeHtml(movie.title)}</h3><p>${escapeHtml(movie.genres)}</p></div><span class="score">${Math.round(movie.score * 100)}<small>% match</small></span>`;
    recommendations.append(article);
  });
}

async function errorMessage(response) {
  try {
    const body = await response.json();
    return body.detail || 'Something went wrong. Please try again.';
  } catch {
    return 'Something went wrong. Please try again.';
  }
}

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle('error', isError);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[character]));
}
