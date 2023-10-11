import overpy
import geopandas as gpd
import ee
from shapely.geometry import Polygon, box
import os
import geemap

api = overpy.Overpass()

# TO DO: Include nodes and relations
# TO DO: Remove duplicates

# TO DO: Change authentication method
# TO DO: Change path to drive
# TO DO: See what can be in a settings file

def get_osm_data():

    # Fetch all wastewater treatment plants within California's boundary
    query = f"""
        area[admin_level=4]["name"="California"]->.searchArea;
        (
        way["man_made"="wastewater_plant"](area.searchArea);
        );
        (._;>;);
        out body;
        """

    result = api.query(query)

    plants = {}

    for way in result.ways:
        # Use the name of the plant or its ID if the name is not available
        plant_name = way.tags.get("name", f"Plant_{way.id}")

        # Extract nodes lat and lon without id
        nodes_coords = [(node.lon, node.lat) for node in way.nodes]

        # get rid of "Decimal"  in the coordinates
        nodes_coords = [tuple(map(float, i)) for i in nodes_coords]
        
        plants[plant_name] = nodes_coords

    # plants_with_official_name = {key: value for key, value in plants.items() if not key.startswith("Plant_")}
    return plants

def convert_geodf(plants):

    geoms = [Polygon(plants[key]) for key in plants]
    df = gpd.GeoDataFrame({'WWTP_name': list(plants.keys()), 'geometry': geoms}, crs="EPSG:4326")

    return df

def download_images(df):

    downloaded_directory = "downloaded_images"
    if not os.path.exists(downloaded_directory):
        os.mkdir(downloaded_directory)

    for idx, row in df[:2].iterrows():

        length = 0.01
        height = 0.01
        center_x = row.centroid.x
        center_y = row.centroid.y

        large_polygon = ee.Geometry.Polygon([(center_x+length, center_y+height), (center_x+length, center_y-height), 
        (center_x-length, center_y-height), (center_x-length, center_y+height)])

        feature = ee.Feature(large_polygon, {})

        collection = (
            ee.ImageCollection("USDA/NAIP/DOQQ")
            .filterDate("2018-01-01", "2019-01-01")
            .select(['R', 'G', 'B'])
        )

        image = ee.Image(collection.mosaic())

        roi = feature.geometry()

        filename = os.path.join(downloaded_directory, f"image.tif")

        image = image.clip(roi).unmask()
        geemap.ee_export_image(
            image, filename=filename, scale=1, region=roi, file_per_band=False
        )

def main():

    osm_data = get_osm_data()
    geodf = convert_geodf(osm_data)

    download_images(geodf)

if __name__ == "__main__":
    main()