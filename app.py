import streamlit as st
import pickle
import requests
import pandas as pd

# TMDB API Key
API_KEY = "332ca506bbd1665dfd9e8ef28d8489b3"

# --------------------- Utility Functions ---------------------

@st.cache_data
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url).json()

        poster_path = response.get('poster_path', '')
        full_poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/200x300?text=No+Image"

        return full_poster_url, response.get('vote_average', 'N/A'), response.get('overview', 'No overview available')
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return "https://via.placeholder.com/200x300?text=No+Image", "N/A", "No overview available"

# Load and merge similarity parts
def load_similarity_parts(num_parts=10):
    all_parts = []
    for i in range(1, num_parts + 1):
        try:
            with open(f"similarity_part{i}.pkl", "rb") as f:
                part = pickle.load(f)
                all_parts.extend(part)
        except FileNotFoundError:
            st.error(f"❌ similarity_part{i}.pkl not found!")
            st.stop()
    return all_parts

# Recommendation logic
def recommend(movie_name):
    try:
        index = movies[movies['title'] == movie_name].index[0]
        distances = sorted(enumerate(similarity[index]), reverse=True, key=lambda x: x[1])

        recommended_movies, recommended_posters, ratings, overviews = [], [], [], []

        for i in distances[1:6]:  # Top 5
            movie_id = movies.iloc[i[0]].id
            title = movies.iloc[i[0]].title
            poster, rating, overview = fetch_movie_details(movie_id)

            recommended_movies.append(title)
            recommended_posters.append(poster)
            ratings.append(rating)
            overviews.append(overview)

        return recommended_movies, recommended_posters, ratings, overviews
    except Exception as e:
        st.error(f"Error in recommendation function: {e}")
        return [], [], [], []

# --------------------- Load Data ---------------------

try:
    movies = pickle.load(open("movies.pkl", "rb"))
    similarity = load_similarity_parts()
    movies_list = movies['title'].values
except FileNotFoundError:
    st.error("❌ Required data files not found (movies.pkl or similarity parts).")
    st.stop()

# --------------------- Streamlit UI ---------------------

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.title("🎥 Movie Recommender System")
st.markdown("Select a movie and discover similar recommendations!")

selected_movie = st.selectbox("🎬 Choose a Movie:", movies_list)

if st.button("🔍 Show Recommendations"):
    movie_names, posters, ratings, overviews = recommend(selected_movie)

    if movie_names:
        cols = st.columns(len(movie_names))
        for i in range(len(movie_names)):
            with cols[i]:
                st.image(posters[i])
                st.markdown(f"**{movie_names[i]}** ⭐ {ratings[i]}")
                st.write(overviews[i][:100] + "...")  # Shortened overview
    else:
        st.warning("No recommendations found. Try a different movie!")
