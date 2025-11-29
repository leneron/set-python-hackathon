import geopandas as gpd
from shapely.geometry import Point
import numpy as np
from sklearn.neighbors import BallTree


def calculate_distances_and_names(candidates, reference_gdf, reference_name_column="Name"):
    """Find the closest location (distance, name) in the reference_gdf to the candidates."""
    candidates_radians = np.radians(np.array(list(candidates.geometry.apply(lambda p: [p.x, p.y]))))
    reference_radians = np.radians(np.array(list(reference_gdf.geometry.apply(lambda p: [p.x, p.y]))))

    tree = BallTree(reference_radians, metric='haversine')

    # Find the closest dist & name
    distances, indices = tree.query(candidates_radians, k=1)
    distances_in_meters = distances * 6371000  # Earth radius, I guess;)
    nearest_names = reference_gdf.iloc[indices.flatten()][reference_name_column].values

    return distances_in_meters, nearest_names

def create_candidates_to_score(grid_step):
    """Create a grid of points anywhere in NY to score."""
    ny_bbox = (-74.259090, 40.477399, -73.700181, 40.917576)  # Межі Нью-Йорка
    lon_values = np.arange(ny_bbox[0], ny_bbox[2], grid_step)
    lat_values = np.arange(ny_bbox[1], ny_bbox[3], grid_step)
    candidate_points = [Point(lon, lat) for lon in lon_values for lat in lat_values]
    return gpd.GeoDataFrame({'geometry': candidate_points}, geometry='geometry')


def get_nicest_locations(rests_parks_metros, grid_step=0.01, metro_weight=2.0, rest_weight=1.0, park_weight=3.0):
    """Find best places in NY according to weitghts."""
    nicerest, parks, metro = rests_parks_metros
    candidates_gdf = create_candidates_to_score(grid_step=grid_step)

    candidates_gdf['dist_to_metro'], candidates_gdf['metro_name']  = calculate_distances_and_names(candidates_gdf, metro)
    candidates_gdf['dist_to_rest'], candidates_gdf["rest_name"] = calculate_distances_and_names(candidates_gdf, nicerest)
    candidates_gdf['dist_to_park'], candidates_gdf["park_name"] = calculate_distances_and_names(candidates_gdf, parks)

    candidates_gdf['score'] = (
            - candidates_gdf['dist_to_metro'] * metro_weight
            - candidates_gdf['dist_to_rest'] * rest_weight
            - candidates_gdf['dist_to_park'] * park_weight
    )

    candidates_gdf = candidates_gdf.sort_values(by='score', ascending=False)

    return candidates_gdf

