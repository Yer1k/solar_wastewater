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

def read_df():

    df = pd.read_csv("/content/combined_epa_hw_WWTP.csv")

    return df

def convert_to_geodf(df):

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
    # gdf["centroid"] = gdf.to_crs('+proj=cea').centroid.to_crs(epsg=4326)
    return gdf

def download_images(df, name):

    # downloaded_directory = settings["download_folder_path"]
    downloaded_directory = f"/content/drive/MyDrive/WWTP_Images_Candidate/{name}"
    if not os.path.exists(downloaded_directory):
        os.mkdir(downloaded_directory)

    for idx, row in df.iterrows():

        filename = os.path.join(downloaded_directory, f"{row['wwtp_name']}.tif")

        if not os.path.exists(filename):

            # what is the unit?
            length = 0.01
            height = 0.01
            center_x = row.geometry.x
            center_y = row.geometry.y
            # print("POINT: ", center_x, center_y)

            large_polygon = ee.Geometry.Polygon([(center_x+length, center_y+height), (center_x+length, center_y-height), 
            (center_x-length, center_y-height), (center_x-length, center_y+height)])

            feature = ee.Feature(large_polygon, {})

            collection = (
                ee.ImageCollection("USDA/NAIP/DOQQ")
                .filterDate("2010-01-01", "2024-01-01")
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

    ee.Authenticate()
    ee.Initialize(project='earth-engine-project-400411')

    df = read_df()

    names = list(set(df["state"]))
    names.remove("California")
    names.remove("Texas")

    for name in names:

        print("NAME START: ", name)

        t_df = df[df["state"] == name]

        gdf = convert_to_geodf(t_df)

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