import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Load preprocessed and cleaned data
@st.cache
def load_data():
    return pd.read_pickle('popular_movies_with_genres_cleaned.pkl')

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

# Display top movies
st.subheader(f"Top {top_n} Movies (Min Ratings: {min_ratings}, Genres: {', '.join(selected_genres)})")
st.write(filtered_movies[['title', 'genres', 'num_ratings', 'avg_rating', 'weighted_rating']])

# Visualization
st.subheader("Top Movies Visualization")
plt.figure(figsize=(10, 6))
sns.barplot(data=filtered_movies, x='weighted_rating', y='title', palette='coolwarm')
plt.title(f"Top {top_n} Movies by IMDb Weighted Rating (Filtered by Genres)")
plt.xlabel("Weighted Rating")
plt.ylabel("Movie Title")
st.pyplot(plt)
