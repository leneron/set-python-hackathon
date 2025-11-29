import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np
from sklearn.neighbors import BallTree
from geo import prepare_data


def calculate_distances(candidates, reference_gdf, radius=1000):
    """
    Обчислює відстань до найближчих точок із reference_gdf для кожної точки кандидатів.
    """
    # Конвертація в радіани (BallTree вимагає радіан для точок координат)
    candidates_radians = np.radians(np.array(list(candidates.geometry.apply(lambda p: [p.x, p.y]))))
    reference_radians = np.radians(np.array(list(reference_gdf.geometry.apply(lambda p: [p.x, p.y]))))

    # Побудова дерева для запитів
    tree = BallTree(reference_radians, metric='haversine')

    # Шукаємо найближчі точки
    distances, _ = tree.query(candidates_radians, k=1)
    # Конвертуємо відстані з радіан у метри (радіус Землі ~6371 км)
    distances_in_meters = distances * 6371000  # Земля в метрах
    return distances_in_meters


def get_nicest_locations(grid_step=0.01, metro_weight=2.0, rest_weight=1.0, park_weight=3.0):
    nicerest, parks, metro = prepare_data()

    ny_bbox = (-74.259090, 40.477399, -73.700181, 40.917576)  # Межі Нью-Йорка
    lon_values = np.arange(ny_bbox[0], ny_bbox[2], grid_step)
    lat_values = np.arange(ny_bbox[1], ny_bbox[3], grid_step)
    candidate_points = [Point(lon, lat) for lon in lon_values for lat in lat_values]
    candidates_gdf = gpd.GeoDataFrame({'geometry': candidate_points}, geometry='geometry')

    candidates_gdf['dist_to_metro'] = calculate_distances(candidates_gdf, metro)
    candidates_gdf['dist_to_rest'] = calculate_distances(candidates_gdf, nicerest)
    candidates_gdf['dist_to_park'] = calculate_distances(candidates_gdf, parks)

    # Розрахунок рейтингу
    # Чим ближче до об'єктів, тим вищий рейтинг
    candidates_gdf['score'] = (
            - candidates_gdf['dist_to_metro'] * metro_weight
            - candidates_gdf['dist_to_rest'] * rest_weight
            - candidates_gdf['dist_to_park'] * park_weight
    )

    candidates_gdf = candidates_gdf.sort_values(by='score', ascending=False)

    return candidates_gdf

