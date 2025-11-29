import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import random
import geo
from geo import prepare_data
from search_for_events import get_nicest_locations


def map_recommendations(m, recommended):
    for _, row in recommended.iterrows():
        score = 450.0 / abs(row["score"])
        if score < 4:
            continue
        if score < 5:
            color = "red"
            popup = f"fair score:{score}"
        elif score < 6:
            color = "orange"
            popup = f"fine score:{score}"
        else:
            color = "green"
            popup = f"good score:{score}"
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=popup,
            icon=folium.Icon(icon="info-circle", prefix='fa', color=color)
        ).add_to(m)


def map_locations(m, locations, name):
    for row in locations:
        if name == "parks":
                color = "green"
                popup = "Park"
                icon="leaf"
        elif name == "restaurants":
                color = "red"
                popup = "Restaurant"
                icon="leaf"
        elif name == "metro":
                color = "blue"
                popup = "Metro"
                icon="train"
        folium.Marker(
            location=[row.y, row.x],
            popup=popup,
            icon=folium.Icon(icon=icon, prefix='fa', color=color, popup=popup)
        ).add_to(m)


def display_map(candidates, restaurants, parks, metro, show_locations=False):
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=12, tiles="Cartodb Positron")

    map_recommendations(m, candidates)
    if show_locations:
        unique_park_locations = candidates['park_location'].unique()
        unique_restaurants_locations = candidates['rest_location'].unique()
        unique_metro_locations = candidates['metro_location'].unique()
        map_locations(m, unique_restaurants_locations, "restaurants")
        map_locations(m, unique_park_locations, "parks")
        map_locations(m, unique_metro_locations, "metro")

    st_folium(m, use_container_width=True)


@st.cache_data
def load_data():
    rests_parks_metros = prepare_data()
    candidates = get_nicest_locations(rests_parks_metros)
    return candidates, *rests_parks_metros


if __name__ == "__main__":
    st.set_page_config(layout='wide')
    st.title("City Pulse Lab")
    candidates, restaurants, parks, metro = load_data()
    display_map(candidates, restaurants, parks, metro, False)

