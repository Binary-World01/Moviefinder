import logging
from flask import Flask, render_template, request, jsonify
import requests
from config import TMDB_API_TOKEN, TMDB_API_BASE_URL

# --- Application Setup ---
app = Flask(__name__)
# Set up basic logging to see errors in the terminal
logging.basicConfig(level=logging.INFO)

# --- API Logic ---
def get_movies_from_tmdb(query):
    """
    Fetches movies from TMDb API and handles potential errors.
    Returns a list of movies or raises an exception.
    """
    if not TMDB_API_TOKEN or "YOUR_API" in TMDB_API_TOKEN:
        logging.error("TMDb API token is not configured.")
        raise ValueError("Server configuration error: API token is missing.")

    search_url = f"{TMDB_API_BASE_URL}/search/movie"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_TOKEN}"
    }
    params = {"query": query}

    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=5)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        return response.json().get('results', [])
    except requests.exceptions.Timeout:
        logging.error("Request to TMDb API timed out.")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred during TMDb API request: {e}")
        raise

# --- Web Routes ---
@app.route('/')
def index():
    """Renders the main search page."""
    return render_template('index.html')

@app.route('/search')
def search_movies():
    """API endpoint to search for movies."""
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "A search query is required."}), 400

    try:
        movies = get_movies_from_tmdb(query)
        return jsonify(movies)
    except ValueError as ve:
        # Handle server-side configuration errors
        return jsonify({"error": str(ve)}), 500
    except requests.exceptions.RequestException:
        # Handle external API or network errors
        return jsonify({"error": "Failed to communicate with the movie service."}), 503
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500

if __name__ == '__main__':
    app.run(debug=True)