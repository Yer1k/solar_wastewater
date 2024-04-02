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

def read_df():
    """
    Read input data consisting of list of candidate wwtp names and coordinates from hydrowaste and epa
    
    Returns:
    df: pandas dataframe consisting of list of candidate wwtp names and coordinates from hydrowaste and epa
    """     
    df = pd.read_csv("../00_source_data/combined_epa_hw_WWTP.csv")

    return df

def write_data_to_csv(df):
    """
    Writes given dataframe to a .csv file
    
    Args:
    df: pandas dataframe
    """   
    df.to_csv("../00_source_data/wwtps.csv")

def download_images(df, name, is_osm):
    """
    Downloads images of WWTPs of type .tif from Earth Engine. It uses either the coordinates given or the centroid coordinates to define a square area around the coordinates of distance 0.02 longitude and latitude units.
    
    Args:
    df: pandas dataframe with wwtp name and coordinates
    name: name of state
    is_osm: True if the data is from OSM (uses centroid of bounding box), False if the data is from hydrowaste and epa (uses given coordinates)
    """   
    # Define directory to store downloaded images
    downloaded_directory = f"../00_source_data/WWTP_Images/{name}"
    # Create directory if it doesn't exist
    if not os.path.exists(downloaded_directory):
        os.mkdir(downloaded_directory)

    # For every wwtp
    for idx, row in df.iterrows():

        # Define path of image file for download
        filename = os.path.join(downloaded_directory, f"{row['wwtp_name']}.tif")

        # If the image doesn't exist
        if not os.path.exists(filename):

            # Define padding to add to coordinates to get square area around wwtp
            # Chosen since most bounding boxes have height and width within 0.02
            length = 0.01
            height = 0.01

            # If the download is for hydrowaste and epa data, use given coordinates
            if not is_osm:
                center_x = row.geometry.x
                center_y = row.geometry.y
            
            # If the download is for OSM data, use bounding box centroid
            else:
                center_x = row.centroid.x
                center_y = row.centroid.y

            # Define square area around the coordinates of wwtp using Polygon object and padding defined above
            large_polygon = ee.Geometry.Polygon([(center_x+length, center_y+height), (center_x+length, center_y-height), 
            (center_x-length, center_y-height), (center_x-length, center_y+height)])

            # Convert Polygon into Feature object
            feature = ee.Feature(large_polygon, {})

            # Define database to download from, date range and channels
            # NAIP dataset: https://developers.google.com/earth-engine/datasets/catalog/USDA_NAIP_DOQQ
            collection = (
                ee.ImageCollection("USDA/NAIP/DOQQ")
                .filterDate("2010-01-01", "2024-01-01")
                .select(['R', 'G', 'B'])
            )

            # Create Image object
            image = ee.Image(collection.mosaic())

            # Get region to download from Feature object
            roi = feature.geometry()

            # Download image with above parameters
            image = image.clip(roi).unmask()
            geemap.ee_export_image(
                image, filename=filename, scale=1, region=roi, file_per_band=False
            )