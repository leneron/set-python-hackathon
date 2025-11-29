from shapely.geometry import Point
import geopandas as gpd
import numpy as np
from sklearn.neighbors import BallTree
from geo import prepare_data


def generate_grid(bbox, spacing=0.0045):
    """
    Створює сітку точок для заданого bounding box (BBox) з визначеним відступом (spacing).
    Spacing задається у градусах (~0.0045 градуса ≈ 500 м).
    """
    minx, miny, maxx, maxy = bbox
    x_coords = np.arange(minx, maxx, spacing)
    y_coords = np.arange(miny, maxy, spacing)
    points = [Point(x, y) for x in x_coords for y in y_coords]
    return gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")


def rate_locations_by_proximity(target_df, sources, radii, weights):
    """
    Оцінює локації (target_df) на основі близькості до джерел (sources).
    sources: список GeoDataFrame (ресторани, метро, парки)
    radii: список радіусів пошуку
    weights: список ваг для кожної категорії
    """
    for source_df, radius, weight, category in zip(sources, radii, weights, ['restaurants', 'parks', 'metro']):
        target_coords = np.array([[geom.x, geom.y] for geom in target_df.geometry])
        source_coords = np.array([[geom.x, geom.y] for geom in source_df.geometry])

        # BallTree для пошуку сусідів
        tree = BallTree(source_coords, metric='haversine')
        counts = tree.query_radius(target_coords, r=radius / 6371000, count_only=True)  # Радіуси в радіанах

        # Додаємо атрибут з оцінками
        target_df[category] = counts * weight

    # Розрахунок сумарного рейтингу
    target_df['total_score'] = target_df[['restaurants', 'parks', 'metro']].sum(axis=1)
    return target_df


def get_nicest_locations():
    # Завантаження даних
    nicerest, parks, metro = prepare_data()

    # Приведення CRS даних до EPSG:4326
    nicerest = nicerest.set_crs("EPSG:4326")
    parks = parks.set_crs("EPSG:4326")
    metro = metro.set_crs("EPSG:4326")

    # BBox Нью-Йорка у EPSG:4326 (широта/довгота)
    bbox = [-74.25909, 40.477399, -73.700272, 40.917577]

    # Генеруємо сітку можливих локацій для Нью-Йорка
    grid_points = generate_grid(bbox, spacing=0.0045)  # Крок сітки у 0.0045 градуса (~500 м)

    # Розрахунок рейтингу локацій
    search_radii = [500, 800, 500]  # Радіуси пошуку в метрах
    category_weights = [1.0, 1.5, 2.0]  # Важливість ресторанів, парків і метро
    sources = [nicerest, parks, metro]

    rated_locations = rate_locations_by_proximity(grid_points, sources, search_radii, category_weights)

    # Сортуємо за сумарним рейтингом
    return rated_locations.sort_values(by='total_score', ascending=False)[:100]
