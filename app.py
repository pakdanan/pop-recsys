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

# Streamlit UI
st.title("Popular Movies Recommender System")
st.markdown("### Based on IMDb Weighted Rating (Cleaned and Precomputed)")

# Sidebar filters
st.sidebar.header("Filters")
selected_genres = st.sidebar.multiselect("Select Genres", all_genres, default=all_genres)
min_ratings = st.sidebar.slider(
    "Minimum Ratings", 
    int(sorted_movies['num_ratings'].min()), 
    int(sorted_movies['num_ratings'].max()), 
    int(sorted_movies['num_ratings'].quantile(0.9))
)
top_n = st.sidebar.slider("Number of Movies to Display", 5, 20, 10)

# Filter by genres
def filter_by_genre(row, genres):
    movie_genres = row['genres'].split('|')
    return any(genre in genres for genre in movie_genres)

filtered_movies = sorted_movies[
    sorted_movies.apply(filter_by_genre, genres=selected_genres, axis=1) &
    (sorted_movies['num_ratings'] >= min_ratings)
].head(top_n)

# Display top movies with posters
st.subheader(f"Top {top_n} Movies (Min Ratings: {min_ratings}, Genres: {', '.join(selected_genres)})")
for _, row in filtered_movies.iterrows():
    col1, col2 = st.columns([1, 3])
    with col1:
        # Fetch and display poster
        poster_url = fetch_poster_url(row['tmdbId'])
        if poster_url:
            st.image(poster_url, width=100)
        else:
            st.image("https://via.placeholder.com/100?text=No+Image", width=100)
    with col2:
        st.write(f"**{row['title']}**")
        st.write(f"Genres: {row['genres']}")
        st.write(f"Number of Ratings: {row['num_ratings']}")
        st.write(f"Average Rating: {row['avg_rating']:.2f}")
        st.write(f"Weighted Rating: {row['weighted_rating']:.2f}")

# Visualization
st.subheader("Top Movies Visualization")
plt.figure(figsize=(10, 6))
sns.barplot(data=filtered_movies, x='weighted_rating', y='title', palette='coolwarm')
plt.title(f"Top {top_n} Movies by IMDb Weighted Rating (Filtered by Genres)")
plt.xlabel("Weighted Rating")
plt.ylabel("Movie Title")
st.pyplot(plt)
