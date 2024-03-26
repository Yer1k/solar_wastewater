import overpy
import geopandas as gpd
import ee
from shapely.geometry import Polygon, box
import os
import geemap
import json
import multiprocessing
import pandas as pd
import math

api = overpy.Overpass()

def get_data(name):

    # Fetch all wastewater treatment plants within California's boundary
    query = f"""
        area[admin_level=4]["name"="{name}"]->.searchArea;
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

    return plants

def read_df():

    df = pd.read_csv("/content/combined_epa_hw_WWTP.csv")

    return df

def convert_to_geodf(plants):

    geoms = [Polygon(plants[key]) for key in plants]
    gdf = gpd.GeoDataFrame({'WWTP_name': list(plants.keys()), 'geometry': geoms}, crs="EPSG:4326")
    gdf["centroid"] = gdf.to_crs('+proj=cea').centroid.to_crs(epsg=4326)
    return gdf

def download_images(df, name):

    # downloaded_directory = settings["download_folder_path"]
    downloaded_directory = f"/content/drive/MyDrive/WWTP_Black_Images/{name}"
    if not os.path.exists(downloaded_directory):
        os.mkdir(downloaded_directory)

    for idx, row in df.iterrows():

        filename = os.path.join(downloaded_directory, f"{row['WWTP_name']}.tif")

        if not os.path.exists(filename):

            # what is the unit?
            length = 0.01
            height = 0.01
            center_x = row.centroid.x
            center_y = row.centroid.y
            # print("POINT: ", center_x, center_y)

            large_polygon = ee.Geometry.Polygon([(center_x+length, center_y+height), (center_x+length, center_y-height), 
            (center_x-length, center_y-height), (center_x-length, center_y+height)])

            feature = ee.Feature(large_polygon, {})

            collection = (
                ee.ImageCollection("USDA/NAIP/DOQQ")
                .filterDate("2000-01-01", "2024-01-01")
                .select(['R', 'G', 'N'])
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

    ee.Authenticate()
    ee.Initialize(project='earth-engine-project-400411')

    # df = read_df()

    names = ["Alaska", "Hawaii"]

    for name in names:

        print("NAME START: ", name)

        plants = get_data(name)

        gdf = convert_to_geodf(plants)

        print(gdf.head())
        print("LENGTH: ", len(gdf))

        a = math.ceil(len(gdf)/4)

        p1 = multiprocessing.Process(target=download_images, args=(gdf[0:a], name)) 
        p2 = multiprocessing.Process(target=download_images, args=(gdf[a:2*a], name)) 
        p3 = multiprocessing.Process(target=download_images, args=(gdf[2*a:3*a], name))
        p4 = multiprocessing.Process(target=download_images, args=(gdf[3*a:], name))

        p1.start() 
        p2.start() 
        p3.start()
        p4.start()

        p1.join() 
        p2.join()
        p3.join()
        p4.join()

        print("NAME END: ", name)

    # download_images(geodf)

if __name__ == "__main__":
    main()