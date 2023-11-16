import overpy
import geopandas as gpd
import ee
from shapely.geometry import Polygon, box
import os
import geemap
import json
import multiprocessing

api = overpy.Overpass()

# TO DO: Include nodes and relations
# TO DO: Remove duplicates

def load_settings():

    global settings

    f = open('settings.json')
    settings = json.load(f)
    f.close()

def get_osm_data():

    # Fetch all wastewater treatment plants within California's boundary
    query = f"""
        area[admin_level=4]["name"="Texas"]->.searchArea;
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
    df["centroid"] = df.to_crs('+proj=cea').centroid.to_crs(epsg=4326)

    return df

def download_images(df):

    # downloaded_directory = settings["download_folder_path"]
    downloaded_directory = "/content/drive/MyDrive/wwtp_images/texas/"
    if not os.path.exists(downloaded_directory):
        os.mkdir(downloaded_directory)

    for idx, row in df.iterrows():

        filename = os.path.join(downloaded_directory, f"{row['WWTP_name']}.tif")

        if not os.path.exists(filename):

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

            image = image.clip(roi).unmask()
            geemap.ee_export_image(
                image, filename=filename, scale=1, region=roi, file_per_band=False
            )

def write_data_to_csv(df):

    # df.to_csv("../data/wwtps.csv")
    df.to_csv("/content/wwtps.csv")

def main():

    # load_settings()
    ee.Initialize()

    osm_data = get_osm_data()
    geodf = convert_geodf(osm_data)

    write_data_to_csv(geodf)

    p1 = multiprocessing.Process(target=download_images, args=(geodf[1600:2000], )) 
    p2 = multiprocessing.Process(target=download_images, args=(geodf[2000:2400], )) 
    p3 = multiprocessing.Process(target=download_images, args=(geodf[2400:2800], ))
    p4 = multiprocessing.Process(target=download_images, args=(geodf[2800:], ))

    p1.start() 
    p2.start() 
    p3.start()
    p4.start()

    p1.join() 
    p2.join()
    p3.join()
    p4.join()

    # download_images(geodf)

if __name__ == "__main__":
    main()