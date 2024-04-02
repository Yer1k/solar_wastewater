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


# Initialize OpenStreetMap (OSM) api
api = overpy.Overpass()

def get_data(name):
    """
    Gets wastewater plants and their coordinates from OSM
    
    Args:
    name: name of state
    
    Returns:
    plants: dictionary of plant names and a corresponding list of bounding box coordinates
    structure: {plant_name: [(longitude1, latitude1), (longitude2, latitude2), ...]}
    """ 
    # Define OSM query of all wastewater plants within state
    query = f"""
        area[admin_level=4]["name"="{name}"]->.searchArea;
        (
        way["man_made"="wastewater_plant"](area.searchArea);
        );
        (._;>;);
        out body;
        """

    # Call OSM api with query to get result
    result = api.query(query)

    plants = {}

    for way in result.ways:
        # Use the name of the plant or its ID if the name is not available
        plant_name = way.tags.get("name", f"Plant_{way.id}")

        # Extract latitude and longitude of nodes of bounding box
        nodes_coords = [(node.lon, node.lat) for node in way.nodes]

        # Convert coordinates into float
        nodes_coords = [tuple(map(float, i)) for i in nodes_coords]

        plants[plant_name] = nodes_coords

    return plants

def convert_to_geodf(plants):
    """
    Converts data from OSM into a geopandas dataframe
    
    Args:
    plants: data dictionary from downloaded from OSM api
    
    Returns:
    gdf: geopandas dataframe with centroid of bounding box from OSM
    """   
    # Converts list of node coordinates into Polygon object
    geoms = [Polygon(plants[key]) for key in plants]
    # Converts OSM data with bounding box Polygon into geopandas dataframe
    gdf = gpd.GeoDataFrame({'WWTP_name': list(plants.keys()), 'geometry': geoms}, crs="EPSG:4326")
    # Gets centroid of Polygon object, by projecting first to '+proj=cea', then back to "EPSG:4326" to account for the curvature of the earth
    gdf["centroid"] = gdf.to_crs('+proj=cea').centroid.to_crs(epsg=4326)

    return gdf

def main():
    """
    Gets data consisting of wwtp names and their bounding box coordinates from OSM and downloads them using google Earth Engine using parallel processing with four processes to speed up the download.
    """
    # Authenticate and initialize earth engine project
    ee.Authenticate()
    ee.Initialize(project='earth-engine-project-400411')

    # Create list of required state names
    names = ["Alaska", "Hawaii"]

    for name in names:

        print("NAME START: ", name)

        # Get data from OSM
        plants = get_data(name)

        # Convert data to geopandas dataframe with centroid of bounding box
        gdf = convert_to_geodf(plants)

        print(gdf.head())
        print("LENGTH: ", len(gdf))

        # Create variable to help divide the dataframe into four
        a = math.ceil(len(gdf)/4)

        # Create four processes and assign the dowload_images function to them
        p1 = multiprocessing.Process(target=utils_download_images.download_images, args=(gdf[0:a], name, True)) 
        p2 = multiprocessing.Process(target=utils_download_images.download_images, args=(gdf[a:2*a], name, True)) 
        p3 = multiprocessing.Process(target=utils_download_images.download_images, args=(gdf[2*a:3*a], name, True))
        p4 = multiprocessing.Process(target=utils_download_images.download_images, args=(gdf[3*a:], name, True))

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