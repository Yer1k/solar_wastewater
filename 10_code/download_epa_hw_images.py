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
from src import utils_download_images

def convert_to_geodf(df):
    """
    Converts given dataframe into a geopandas dataframe
    
    Args:
    df: pandas dataframe with latitude and longitude
    
    Returns:
    gdf: geopandas dataframe with Point object from latitude and longitude
    """        
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
    return gdf

def main():
    """
    Reads input data consisting of candidate wwtp names and their coordinates and downloads them using google Earth Engine using parallel processing with four processes to speed up the download.
    """
    # Authenticate and initialize earth engine project
    ee.Authenticate()
    ee.Initialize(project='earth-engine-project-400411')

    # Read input data with candidate wwtp names and their coordinates
    df = utils_download_images.read_df()

    # Get list of state names
    names = list(set(df["state"]))
    # names.remove("California")
    # names.remove("Texas")

    for name in names:

        print("NAME START: ", name)

        # Filter dataframe based on state name
        t_df = df[df["state"] == name]

        # Convert dataframe to geopandas dataframe
        gdf = convert_to_geodf(t_df)

        print(gdf.head())
        print("LENGTH: ", len(gdf))

        # Create variable to help divide the dataframe into four
        a = math.ceil(len(gdf)/4)

        # Create four processes and assign the dowload_images function to them
        p1 = multiprocessing.Process(target=utils_download_images.download_images, args=(gdf[0:a], name, False)) 
        p2 = multiprocessing.Process(target=utils_download_images.download_images, args=(gdf[a:2*a], name, False)) 
        p3 = multiprocessing.Process(target=utils_download_images.download_images, args=(gdf[2*a:3*a], name, False))
        p4 = multiprocessing.Process(target=utils_download_images.download_images, args=(gdf[3*a:], name, False))

        # Start processes
        p1.start() 
        p2.start() 
        p3.start()
        p4.start()

        # Wait for processes to finish
        p1.join() 
        p2.join()
        p3.join()
        p4.join()

        print("NAME END: ", name)

    # download_images(geodf)

if __name__ == "__main__":
    main()