import geopandas
import geodatasets

gdf = geopandas.read_file('~/dev/set-python-hackathon/data/MTA_Subway_Stations_20251129.csv')

print(gdf)