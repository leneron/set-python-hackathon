import os
import pandas as pd
import geopandas as gpd
from shapely import wkt

DATA_DIR = "../data"
METRO_FILEPATH = DATA_DIR + os.sep + "MTA_Subway_Stations_20251129.csv"
RESTAURANTS_FILEPATH = DATA_DIR + os.sep + "DOHMH_New_York_City_Restaurant_Inspection_Results_20251129.csv"
VIOLATIONS_FILEPATH = DATA_DIR + os.sep + "nyc_restaurant_dohmh_20251129.csv"
PARKS_FILEPATH = DATA_DIR + os.sep + "parks.csv"

def safe_wkt_loads(location):
    try:
        return wkt.loads(location)
    except Exception:
        return None
    
def geometry_wkt_to_point_wkt(geometry_wkt: str):
    if pd.isna(geometry_wkt):
        return None
    try:
        geometry = wkt.loads(geometry_wkt)
    except Exception:
        return None
    try:
        point = geometry.representative_point()
        return f"POINT ({point.x} {point.y})"
    except Exception:
        return None

def get_entities_from_csv(
        filepath: str,
        source_columns: tuple,
        df_columns: tuple = ("Name", "Location"),
        polygon_to_location: bool = False
) -> gpd.GeoDataFrame:
    """Get names and locations from CSV."""
    df = gpd.read_file(filepath, columns=source_columns)
    if df_columns:
        df.columns = df_columns
    if polygon_to_location:
        df["Location"] = df["Location"].apply(geometry_wkt_to_point_wkt)       
    df["geometry"] = df["Location"].apply(safe_wkt_loads)
    geo_df = gpd.GeoDataFrame(df, geometry="geometry")
    geo_df = geo_df[geo_df.geometry.notna()]
    return geo_df

def prepare_data() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Collect entities for provided CSV files."""
    metro_locations = get_entities_from_csv(
        filepath=METRO_FILEPATH,
        source_columns=('Stop Name', 'Georeference')
    )

    restaurants_locations = get_entities_from_csv(
        filepath=RESTAURANTS_FILEPATH,
        source_columns=('DBA', 'VIOLATION CODE', 'Location'),
        df_columns=("Name", "ViolationCode", "Location")
    )

    nice_restaurants_locations = restaurants_locations.loc[
        (restaurants_locations["ViolationCode"].isna()) | (restaurants_locations["ViolationCode"] == ""),
        ["Name", "Location", "geometry"]
    ]

    print(f"Only {len(nice_restaurants_locations)}/{len(restaurants_locations)} restaurants seem to be nice")

    parks_locations = get_entities_from_csv(
        filepath=PARKS_FILEPATH,
        source_columns=('SIGNNAME', 'Location'),
        polygon_to_location=True
    )

    return nice_restaurants_locations,  parks_locations, metro_locations
