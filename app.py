import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import tmdbsimple as tmdb

# TMDb API key setup
tmdb.API_KEY = '07e4f042769f354fb3611f2cb3b0124d'  # Replace with your TMDb API key

# Load preprocessed and cleaned data
@st.cache
def load_data():
    return pd.read_pickle('popular_movies.pkl')

# Function to fetch poster URL using tmdbsimple
def fetch_poster_url(tmdb_id):
    """Fetch the poster URL for a movie using its TMDb ID."""
    try:
        if tmdb_id == 0:  # Skip if tmdbId is missing
            return None
        movie = tmdb.Movies(tmdb_id)
        response = movie.info()
        poster_path = response.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w200{poster_path}"
    except Exception as e:
        st.error(f"Error fetching poster for TMDb ID {tmdb_id}: {e}")
    return None

# Load data
sorted_movies = load_data()

# Extract unique genres
all_genres = sorted_movies['genres'].str.split('|').explode().unique()

# Sidebar filters
st.sidebar.header("Filters")
selected_genres = st.sidebar.multiselect("Select Genres", all_genres, default=all_genres)
min_ratings = st.sidebar.slider(
    "Minimum Ratings", 
    int(sorted_movies['num_ratings'].min()), 
    int(sorted_movies['num_ratings'].max()), 
    int(sorted_movies['num_ratings'].quantile(0.9))
)
top_n = st.sidebar.slider("Number of Movies to Display", 5, 12, 9)

# Filter by genres
def filter_by_genre(row, genres):
    movie_genres = row['genres'].split('|')
    return any(genre in genres for genre in movie_genres)

filtered_movies = sorted_movies[
    sorted_movies.apply(filter_by_genre, genres=selected_genres, axis=1) &
    (sorted_movies['num_ratings'] >= min_ratings)
].head(top_n)

# Display movies in grid format
st.subheader(f"Top {top_n} Movies ( Based on IMDb Weighted Rating )")
cols_per_row = 3  # Number of columns per row
rows = [filtered_movies.iloc[i:i + cols_per_row] for i in range(0, len(filtered_movies), cols_per_row)]

for row in rows:
    columns = st.columns(cols_per_row)
    for col, (_, movie) in zip(columns, row.iterrows()):
        poster_url = fetch_poster_url(movie['tmdbId'])
        with col:
            if poster_url:
                st.image(poster_url, width=150)
            else:
                st.image("https://via.placeholder.com/150?text=No+Image", width=150)
            st.caption(movie['title'])


# Visualization
st.subheader("Top Movies Visualization")
plt.figure(figsize=(10, 6))
sns.barplot(data=filtered_movies, x='weighted_rating', y='title', palette='coolwarm')
plt.title(f"Top {top_n} Movies by IMDb Weighted Rating (Filtered by Genres)")
plt.xlabel("Weighted Rating")
plt.ylabel("Movie Title")
st.pyplot(plt)
