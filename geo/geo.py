import geopandas

DATA_DIR = "../data/"

subway = geopandas.read_file(f'{DATA_DIR}/MTA_Subway_Stations_20251129.csv')
parks = geopandas.read_file(f'{DATA_DIR}/Parks_Properties_20251129.csv')
restaurants = geopandas.read_file(f'{DATA_DIR}/nyc_restaurant_dohmh_20251129.csv')
restaurants_insp = geopandas.read_file(f'{DATA_DIR}/DOHMH_New_York_City_Restaurant_Inspection_Results_20251129.csv')


print(subway)
print(parks)
print(restaurants)
print(restaurants_insp)