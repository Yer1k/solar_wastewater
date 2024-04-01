import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt
import ast
from scipy.spatial import cKDTree
from geopy.distance import geodesic


def state_name_abbrev_pair():
    """
    Return a dictionary that maps state names to state abbreviations

    Input:
    - None

    Output:
    - state_pair: dictionary that maps state names to state abbreviations
        - Key: state name
        - Value: state abbreviation
    """
    state_pair = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
    }

    return state_pair


def read_HydroWaste_data(HydroWaste_path, us_boundary_path):
    """
    Read HydroWaste data, filter out the data points that are not in the US, and return a dataframe with columns:
    - hw_WWTP_NAME: name of the WWTP
    - hw_lat: latitude of the WWTP
    - hw_lon: longitude of the WWTP
    - state: state where the WWTP is located

    Input:
    - HydroWaste_path: path to the HydroWaste data
    - us_boundary_path: path to the US boundary shapefile

    Output:
    - df_hw_us: dataframe with columns hw_WWTP_NAME, hw_lat, hw_lon, state
    """
    hw_data = pd.read_csv(HydroWaste_path, encoding="latin1")
    hw_us = hw_data[hw_data["COUNTRY"] == "United States"]
    gdf_hw_us = gpd.GeoDataFrame(
        hw_us, geometry=gpd.points_from_xy(hw_us.LON_WWTP, hw_us.LAT_WWTP)
    )
    gdf_hw_us.crs = {"init": "epsg:4326"}
    gdf_hw_us.reset_index(drop=True, inplace=True)

    us_boundary = gpd.read_file(us_boundary_path)
    gdf_hw_us = gdf_hw_us.to_crs(us_boundary.crs)
    gdf_hw_us = gpd.sjoin(gdf_hw_us, us_boundary, how="inner", op="within")
    df_hw_us = gdf_hw_us.loc[
        :, ["WWTP_NAME", "LAT_WWTP", "LON_WWTP", "NAME", "geometry"]
    ]
    df_hw_us.columns = ["hw_WWTP_NAME", "hw_lat", "hw_lon", "state", "geometry"]
    return df_hw_us


def read_EPA_data(EPA_path):
    """
    Read EPA data, filter out the data points that are not WWTP, and return a dataframe with columns:
    - CWP_NAME: name of the WWTP
    - CWP_STATE: state where the WWTP is located
    - geometry: geometry of the WWTP
    - epa_lon: longitude of the WWTP
    - epa_lat: latitude of the WWTP

    Input:
    - EPA_path: path to the EPA data

    Output:
    - epa_WWTP: dataframe with columns CWP_NAME, CWP_STATE, geometry, epa_lon, epa_lat
    """
    df_epa = gpd.read_file(EPA_path)
    df_epa = df_epa.to_crs(epsg=4326)
    gpd_epa = df_epa.loc[:, ["CWP_NAME", "CWP_STATE", "geometry"]]
    epa_WWTP = gpd_epa[gpd_epa["CWP_NAME"].str.contains("WWTP|WWTF|STP|WQCF|WRP|WWRF")]
    epa_WWTP.drop_duplicates(inplace=True)
    epa_WWTP.reset_index(drop=True, inplace=True)
    epa_WWTP.loc[:, "epa_lon"] = epa_WWTP.geometry.x
    epa_WWTP.loc[:, "epa_lat"] = epa_WWTP.geometry.y
    return epa_WWTP


def read_osm_data(osm_path):
    """
    Read manually tagged OSM data and return a dataframe with columns:
    - osm_name: name of the WWTP
    - osm_longitude: longitude of the WWTP
    - osm_latitude: latitude of the WWTP
    """

    def extract_lon_lat(centroid_str):
        """
        Extract longitude and latitude from the centroid string

        Input:
        - centroid_str: centroid string

        Output:
        - lon: longitude
        - lat: latitude
        """
        clean_str = centroid_str.replace("POINT (", "").replace(")", "")
        lon, lat = map(float, clean_str.split(" "))
        return lon, lat

    df_osm = pd.read_csv(
        osm_path,
    )
    df_osm["osm_longitude"], df_osm["osm_latitude"] = zip(
        *df_osm["centroid"].apply(extract_lon_lat)
    )
    df_osm = df_osm.drop(columns=["centroid"])
    df_osm.reset_index(drop=True, inplace=True)
    return df_osm


def plt_world_map(gdf, us_boundary, color, title):
    """
    Plot the WWTP data on a world map

    Input:
    - gdf: geodataframe with WWTP data
    - us_boundary: geodataframe with US boundary
    - color: color of the WWTP data points
    - title: title of the plot
    """

    fig, ax = plt.subplots()
    fig.set_size_inches(20, 20)
    us_boundary.plot(ax=ax, color="lightgrey", alpha=0.5, edgecolor="grey")
    gdf.plot(ax=ax, color=color, markersize=2)
    # set x and y axis limits
    ax.set_xlim(-128, -65)
    ax.set_ylim(24, 50)
    plt.title(title, fontsize=20)
    plt.axis("off")
    plt.show()


def statewise_WWTP_count(
    hw_df, target_df, target_df_name, state_name_abbrev_pair, hw_color, target_color
):
    WWTP_num = pd.DataFrame()
    for state_, state in state_name_abbrev_pair.items():
        hw_num = len(hw_df[hw_df["state"] == state_])
        if target_df_name == "epa":
            target_num = len(target_df[target_df["CWP_STATE"] == state])
        elif target_df_name == "osm":
            target_num = len(target_df[target_df["state"] == state_])
        WWTP_num = pd.concat(
            [
                WWTP_num,
                pd.DataFrame(
                    {
                        "state": [state],
                        "hw_num": [hw_num],
                        f"{target_df_name}_num": [target_num],
                    }
                ),
            ]
        )
    if target_df_name == "osm":
        WWTP_num.loc[WWTP_num["state"] == "CA", f"{target_df_name}_num"] = 116 + 183
        WWTP_num.loc[WWTP_num["state"] == "TX", f"{target_df_name}_num"] = 198 + 104
    WWTP_num.reset_index(drop=True, inplace=True)

    # print the number of WWTPs in each state
    print(f"Number of WWTPs in the US from HydroWASTE: ", len(hw_df))
    print(f"Number of WWTPs in the US from {target_df_name}: ", len(target_df))
    print(
        "Number of state where HydroWASTE has more WWTPs: ",
        len(WWTP_num[WWTP_num["hw_num"] > WWTP_num[f"{target_df_name}_num"]]),
    )
    print(
        "State where HydroWASTE has more WWTPs: ",
        WWTP_num[WWTP_num["hw_num"] > WWTP_num[f"{target_df_name}_num"]][
            "state"
        ].values,
    )

    # sort by HydroWASTE number
    sorted_wwtp_num = WWTP_num.sort_values(by="hw_num", ascending=False)
    sorted_wwtp_num.plot(
        x="state",
        y=["hw_num", f"{target_df_name}_num"],
        kind="bar",
        figsize=(18, 8),
        color=[hw_color, target_color],
    )
    # start plotting
    plt.legend(["HydroWASTE", f"{target_df_name.upper()}"], fontsize=15)
    plt.grid(axis="y", linestyle="--", alpha=0.7, color="grey")
    plt.title(
        f"Number of WWTPs in each state from HydroWASTE and {target_df_name.upper()}",
        fontsize=20,
    )
    plt.xlabel("State", fontsize=15)
    plt.ylabel("Number of WWTPs", fontsize=15)
    plt.show()
    return sorted_wwtp_num


def closest_point(point, points):
    """
    Find closest point from a list of points.

    Input:
    - point: a given point
    - points: a list of points

    Output:
    - the closest point in the list of points to the given point
    """
    return points[cKDTree(points).query(point)[1]]


def calculate_distance(
    row,
    lat_col_1="hw_lat",
    lon_col_1="hw_lon",
    lat_col_2="epa_lat",
    lon_col_2="epa_lon",
):
    """
    Calculate the distance between two points

    Input:
    - row: row of a dataframe
    - lat_col_1: column name of the latitude of the first point
    - lon_col_1: column name of the longitude of the first point
    - lat_col_2: column name of the latitude of the second point
    - lon_col_2: column name of the longitude of the second point

    Output:
    - distance: distance between the two points
    """
    points_1 = (row[lat_col_1], row[lon_col_1])
    points_2 = (row[lat_col_2], row[lon_col_2])
    return geodesic(points_1, points_2).kilometers


def find_closest_point(
    source_df, target_df, source_lat_col, source_lon_col, target_lat_col, target_lon_col
):
    """
    Find the closest point in the target dataframe for each point in the source dataframe

    Input:
    - source_df: dataframe with the source points
    - target_df: dataframe with the target points
    - source_lat_col: column name of the latitude of the source points
    - source_lon_col: column name of the longitude of the source points
    - target_lat_col: column name of the latitude of the target points
    - target_lon_col: column name of the longitude of the target points

    Output:
    - source_df: dataframe with the closest points in the target dataframe
    """
    source_points = list(zip(source_df[source_lon_col], source_df[source_lat_col]))
    target_points = list(zip(target_df[target_lon_col], target_df[target_lat_col]))
    closest_target_points = [closest_point(p, target_points) for p in source_points]
    source_df[target_lon_col], source_df[target_lat_col] = zip(*closest_target_points)
    source_df["distance"] = source_df.apply(
        lambda row: calculate_distance(
            row,
            source_lat_col,
            source_lon_col,
            target_lat_col,
            target_lon_col,
        ),
        axis=1,
    )
    source_df.sort_values(by="distance", ascending=True, inplace=True)
    source_df.reset_index(drop=True, inplace=True)
    return source_df


def statewise_closest_points(state_name, state_name_abbrev_pair, epa, hw):
    """
    Calculate the closest EPA WWTP for each HW WWTP in a given state, and return two outputs:
    - hw_subset: dataframe with columns
        - hw_WWTP_NAME: name of the HW WWTP
        - hw_lat: latitude of the HW WWTP
        - hw_lon: longitude of the HW WWTP
        - state: state where the HW WWTP is located
        - epa_lon: longitude of the closest EPA WWTP
        - epa_lat: latitude of the closest EPA WWTP
        - epa_name: name of the closest EPA WWTP
        - distance: distance between the HW WWTP and the closest EPA WWTP
    - summary_table: list with the following values:
        - number of HW WWTPs in the state
        - number of EPA WWTPs in the state
        - number of HW WWTPs that are within 1 km of its closest EPA WWTP

    Input:
    - state_name: name of the state
    - state_name_abbrev_pair: dictionary that maps state names to state abbreviations
    - epa: dataframe with EPA WWTP data
    - hw: dataframe with HW WWTP data

    Output:
    - hw_subset: dataframe with columns hw_WWTP_NAME, hw_lat, hw_lon, state, epa_lon, epa_lat, epa_name, distance
    - summary_list: list with the count of HW WWTPs, EPA WWTPs, and HW WWTPs within 1 km of its closest EPA WWTP
    """
    hw_state = state_name
    epa_state = state_name_abbrev_pair[state_name]

    hw_subset = hw[hw["state"] == hw_state]
    hw_subset.reset_index(drop=True, inplace=True)
    print(f"Number of HW WWTPs in {hw_state}: {hw_subset.shape[0]}")
    epa_subset = epa[epa["CWP_STATE"] == epa_state]
    epa_subset.reset_index(drop=True, inplace=True)
    print(f"Number of EPA WWTPs in {epa_state}: {epa_subset.shape[0]}")

    hw_subset = find_closest_point(
        hw_subset, epa_subset, "hw_lat", "hw_lon", "epa_lat", "epa_lon"
    )
    print(
        f"Out of {hw_subset.shape[0]} HW WWTPs, {hw_subset[hw_subset['distance'] < 1].shape[0]} are within 1 km of its closest EPA WWTP."
    )
    print("-" * 50)

    summary_list = [
        len(hw_subset),
        len(epa_subset),
        hw_subset[hw_subset["distance"] < 1].shape[0],
    ]
    return hw_subset, summary_list
