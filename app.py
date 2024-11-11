import pickle
import pandas as pd
import streamlit as st
import requests

import time

def fetch_poster(movie_id, retries=3):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3360f9755f566d55c89c68ef6541687d&language=en-US"
    for _ in range(retries):
        try:
            data = requests.get(url, timeout=10)
            data.raise_for_status()
            data = data.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                return None
        except requests.exceptions.Timeout:
            print(f"Timeout error. Retrying...")
            time.sleep(3)  # Wait for 3 seconds before retrying
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            break
    return None


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

st.header('Movie Recommender System')

# Load the pickle files
try:
    movies = pickle.load(open('movies_dictionary.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    
    # Convert the dictionary to a DataFrame
    if isinstance(movies, dict):
        movies = pd.DataFrame(movies)
except FileNotFoundError as e:
    st.error("Pickle files not found. Please check your file paths.")

# Check if the 'title' column exists in DataFrame
if 'title' not in movies.columns:
    st.error("'title' column not found in the movies DataFrame.")
else:
    movie_list = movies['title'].values
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list
    )

    if st.button('Show Recommendation'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
        cols = st.columns(5)  # Updated to st.columns
        for i, col in enumerate(cols):
            col.text(recommended_movie_names[i])
            if recommended_movie_posters[i]:
                col.image(recommended_movie_posters[i])
            else:
                col.text("Poster not available.")
