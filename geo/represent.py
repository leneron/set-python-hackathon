import streamlit as st
import folium
from streamlit_folium import st_folium

from geo import prepare_data
from search_for_events import get_nicest_locations


def display_map(locations):
    print(f"Displaying map with {len(locations)} locations.")
    # Створюємо базову карту
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)  # Центр карти (наприклад, Нью-Йорк)

    # Додаємо метро на мапу
    for _, row in locations.iterrows():
        if row["total_score"] < 30:
            continue
        if row["total_score"] < 50:
            color = "red"
            popup = "Fair"
        elif row["total_score"] < 70:
            color = "yellow"
            popup = "Fine"
        else:
            color = "green"
            popup = "Nice!"
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5,
            popup=popup,
            color=color,
            fill=True,
            fill_color=color
        ).add_to(m)

    # Відображення мапи через streamlit-folium
    st.title("Maps of Entities")
    st_folium(m, width=700, height=500)


# Приклад запуску (замініть на ваші дані)
if __name__ == "__main__":
    display_map(get_nicest_locations())
