import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import seaborn as sns
import ast
from scipy.spatial import cKDTree
from geopy.distance import geodesic
from rasterio.plot import show
import statsmodels.api as sm


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


def osm2gdf(osm_path):
    """
    Read manually tagged OSM data and return a geodataframe

    Input:
    - osm_path: path to the OSM data file

    Output:
    - gdf_osm: geodataframe of the OSM data

    """

    df_osm = read_osm_data(osm_path)
    gdf_osm = gpd.GeoDataFrame(
        df_osm,
        geometry=gpd.points_from_xy(df_osm.osm_longitude, df_osm.osm_latitude),
    )
    gdf_osm.crs = "EPSG:4326"
    return gdf_osm


def read_client_data(client_data_path):
    """
    Read client data and return a geodataframe

    Input:
    - client_data_path: path to the client data file

    Output:
    - gdf_client: geodataframe of the client data

    """

    df_client = pd.read_excel(client_data_path)
    df_client = df_client.loc[:, ["FacilityName", "Lat, Long"]]
    df_client["lat"] = df_client["Lat, Long"].apply(lambda x: float(x.split(",")[0]))
    df_client["lon"] = df_client["Lat, Long"].apply(lambda x: float(x.split(",")[1]))
    df_client.drop(columns=["Lat, Long"], inplace=True)

    # convert to geodataframe
    gdf_client = gpd.GeoDataFrame(
        df_client, geometry=gpd.points_from_xy(df_client.lon, df_client.lat)
    )
    gdf_client.crs = "epsg:4326"
    return gdf_client


def interactive_map(df):
    """
    Create an interactive map with the given dataframe

    Input:
    - df: dataframe with osm data

    Output:
    - m: interactive map with the given data
    """
    import folium
    from folium.plugins import MarkerCluster
    from folium.plugins import FastMarkerCluster

    # Create a map
    m = folium.Map(zoom_start=6)

    # Add points to the map
    mc = MarkerCluster()
    for idx, row in df.iterrows():
        mc.add_child(
            folium.Marker(location=[row["osm_latitude"], row["osm_longitude"]])
        )
    m.add_child(mc)
    return m


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
    """
    Calculate the number of WWTPs in each state from HydroWASTE and the target dataset, and plot the results

    Input:
    - hw_df: dataframe with HydroWASTE data
    - target_df: dataframe with the target data
    - target_df_name: name of the target dataset
    - state_name_abbrev_pair: dictionary that maps state names to state abbreviations
    - hw_color: color of the HydroWASTE data
    - target_color: color of the target data

    Output:
    - sorted_wwtp_num: dataframe with the number of WWTPs in each state from HydroWASTE and the target dataset
    """
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


def state_county_boundary(state_name):
    """
    Retreive the boundary of the state and counties in the state

    Input:
    - state_name: name of the state

    Output:
    - state_boundary: boundary of the state
    - counties_boundary: boundary of the counties in the state
    """
    # URLs to shapefiles
    url_state = "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_state_5m.zip"
    url_counties = (
        "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_county_5m.zip"
    )

    # Load data
    all_states = gpd.read_file(url_state)
    all_counties = gpd.read_file(url_counties)

    if state_name == "California":
        state_boundary = all_states[all_states["STUSPS"] == "CA"]
        counties_boundary = all_counties[all_counties["STATEFP"] == "06"]

    elif state_name == "Texas":
        state_boundary = all_states[all_states["STUSPS"] == "TX"]
        counties_boundary = all_counties[all_counties["STATEFP"] == "48"]

    state_boundary.to_crs(epsg=4326, inplace=True)
    counties_boundary.to_crs(epsg=4326, inplace=True)
    return state_boundary, counties_boundary


def merge_income_pop_boundary(state_boundary_path, income_path, pop_path, state_name):
    """
    Merge the income and population data with the state boundary data

    Input:
    - state_boundary_path: path to the state boundary shapefile
    - income_path: path to the income data
    - pop_path: path to the population data
    - state_name: name of the state

    Output:
    - gdf_MCD_pop_income: geodataframe with the merged data
    """
    gdf_mcd = gpd.read_file(state_boundary_path)
    gdf_mcd = gdf_mcd.to_crs(epsg=4326)

    pop = pd.read_csv(pop_path)
    pop = pop.transpose()
    pop = pop.reset_index()
    pop = pop.iloc[1:]
    pop.columns = ["Name", "population"]
    pop.fillna(0, inplace=True)
    pop.loc[:, "Name"] = pop.loc[:, "Name"].str.split(",").str[0]
    pop.loc[:, "population"] = pop.loc[:, "population"].str.replace(",", "")
    pop["population"] = (
        pd.to_numeric(pop["population"], errors="coerce").fillna(0).astype(int)
    )

    income = pd.read_csv(income_path)
    income = income.transpose()
    income = income.reset_index()
    income = income.iloc[1:]
    income.columns = ["Name", "income"]
    income.loc[:, "Name"] = income.loc[:, "Name"].str.split(",").str[0]
    income.income = income.income.str.replace(",", "")
    income.fillna(0, inplace=True)
    income.income = income.income.astype(int)

    # merge population and income data
    pop_income = pd.merge(pop, income, on="Name")

    # merge with gdf_CA_MCD
    if state_name == "California":
        gdf_MCD_pop_income = pd.merge(
            gdf_mcd, pop_income, left_on="NAMELSAD", right_on="Name"
        )
    elif state_name == "Texas":
        pop_income["Name"] = pop_income["Name"].str.split(" ").str[:-1].str.join(" ")
        gdf_MCD_pop_income = pd.merge(
            gdf_mcd, pop_income, left_on="CITY_NM", right_on="Name"
        )

    return gdf_MCD_pop_income


def plt_state_socioeconomic_map(
    merged_gdf, wwtp_gdf, state_boudary, counties_boundary, title, column, cmap
):
    """
    Plot the state socioeconomic data on a map

    Input:
    - gdf: geodataframe with state socioeconomic data
    - wwtp_gdf: geodataframe with WWTP locations
    - state_boudary: geodataframe with state boundary
    - counties_boundary: geodataframe with county boundary
    - column: column name of the socioeconomic data
    - title: title of the plot
    - cmap: color map
    """

    # plot the plants in three different markers, the background is the population
    fig, ax = plt.subplots(figsize=(15, 15))
    state_boudary.plot(ax=ax, facecolor="none", edgecolor="black")
    counties_boundary.plot(ax=ax, facecolor="none", edgecolor="dimgrey", linewidth=0.5)
    merged_gdf.plot(ax=ax, column=column, cmap=cmap, edgecolor="black", linewidth=0.2)
    wwtp_gdf.plot(
        ax=ax, marker="s", color="red", markersize=5, label="Verified WWTPs from OSM"
    )

    # Adjust the legend and color bar
    sm = plt.cm.ScalarMappable(
        cmap=cmap,
        norm=plt.Normalize(
            vmin=merged_gdf[column].min(), vmax=merged_gdf[column].max()
        ),
    )
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, shrink=0.5)  # Adjust the shrink parameter as needed
    cbar.set_label("Population", rotation=270, labelpad=20)

    # Set title
    plt.title(title, fontsize=20)
    plt.axis("off")
    plt.legend(fontsize=15)
    plt.show()


def pop_income_boxplot(merged_gdf, wwtp_gdf):
    """
    Plot boxplots for the number of WWTP vs population and median income

    Input:
    - merged_gdf: geodataframe with merged data (population and income)
    - wwtp_gdf: geodataframe with WWTP locations

    Output:
    - boxplots for the number of WWTP vs population and median income
    """
    merged_gdf["counts"] = merged_gdf["geometry"].apply(
        lambda x: wwtp_gdf.within(x).sum()
    )

    # Plot setup
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

    # Boxplot for counts vs population
    sns.boxplot(x="counts", y="population", data=merged_gdf, ax=ax1, palette="YlGn")
    ax1.set_xlabel("Number of WWTP", fontsize=14)
    ax1.set_ylabel("Population", fontsize=14)
    ax1.set_title("Number of WWTP vs Population", fontsize=16)

    # Boxplot for counts vs income
    sns.boxplot(x="counts", y="income", data=merged_gdf, ax=ax2, palette="YlGn")
    ax2.set_xlabel("Number of WWTP", fontsize=14)
    ax2.set_ylabel("Median Income", fontsize=14)
    ax2.set_title("Number of WWTP vs Median Income", fontsize=16)

    plt.show()


def wwtp_with_pop_distribution(wwtp, gridded_pop, color, colormap, title):
    """
    Plot the WWTP data on a map with the gridded population data

    Input:
    - wwtp: geodataframe with WWTP list
    - gridded_pop: rasterio dataset with gridded population data
    - color: color of the WWTP data points
    - colormap: colormap for the gridded population data
    - title: title of the plot

    Output:
    - plot of the WWTP data on a map with the gridded population data
    """
    fig, ax = plt.subplots(figsize=(20, 20))

    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)

    # mask the no data values
    gridded_pop_data = gridded_pop.read(1, masked=True)
    # change no data values to 0
    gridded_pop_data = np.nan_to_num(gridded_pop_data)

    # add a small number to avoid log(0)
    err = 1e-6
    vmin = gridded_pop_data.min() + err
    vmax = gridded_pop_data.max()
    norm = colors.LogNorm(vmin=vmin, vmax=vmax)

    show(gridded_pop, ax=ax, cmap=colormap, norm=norm)
    cbar = plt.colorbar(mappable=plt.cm.ScalarMappable(cmap=colormap, norm=norm), ax=ax)

    # plot the wwtp
    wwtp.plot(ax=ax, color=color, markersize=2)
    plt.title(title, fontsize=20)
    plt.show()


def process_state_data(path, column_name):
    """
    Read and process the socioeconomic data for US states

    Input:
    - path: path to the data
    - column_name: column name of the data

    Output:
    - statewise_df: dataframe with the processed data
    """
    statewise_df = pd.read_csv(path)
    if column_name == "population":
        statewise_df = statewise_df.iloc[1, :]
    elif column_name == "income":
        statewise_df = statewise_df.iloc[0, :]
    statewise_df = statewise_df.reset_index()
    statewise_df.columns = ["state", column_name]
    statewise_df = statewise_df.iloc[1:, :]
    # only keep rows with Estimate in the state column
    if column_name == "population":
        statewise_df = statewise_df.loc[statewise_df["state"].str.contains("Estimate")]
        statewise_df["state"] = statewise_df["state"].str.replace("!!Estimate", "")
    elif column_name == "income":
        statewise_df = statewise_df.loc[
            statewise_df["state"].str.contains("!!Households!!Estimate")
        ]
        statewise_df["state"] = statewise_df["state"].str.replace(
            "!!Households!!Estimate", ""
        )
    # all capital letters for state
    statewise_df["state"] = statewise_df["state"].str.upper()
    statewise_df.reset_index(drop=True, inplace=True)
    statewise_df[column_name] = statewise_df[column_name].str.replace(",", "")
    statewise_df[column_name] = statewise_df[column_name].astype(int)
    return statewise_df


def plt_pop_income_wwtp(merged_df, title, ax, column_name):
    """
    Plot the number of WWTPs vs population and total household income

    Input:
    - merged_df: dataframe with merged data
    - title: title of the plot
    - ax: axis to plot
    - column_name: column name of the data

    Output:
    - plot of the number of WWTPs vs population and total household income
    """
    sns.scatterplot(
        data=merged_df,
        x="income",
        y=column_name,
        ax=ax,
        size="population",
        hue="population",
        sizes=(10, 250),
        palette="Blues",
        edgecolor="black",
    )
    ax.set_xlabel("Total Household Income", fontsize=15)
    ax.set_ylabel("Number of WWTPs", fontsize=15)
    ax.set_title(title, fontsize=20)
    ax.legend(title="Population", fontsize=10)


def lr_analysis(merged_df, x_col, y_col, x_label, y_label, titte, if_plt=True):
    """
    Perform linear regression analysis and plot the results

    Input:
    - merged_df: dataframe with merged data, including x_col and y_col
    - x_col: column name of the independent variable
    - y_col: column name of the dependent variable'
    - x_label: label of the independent variable
    - y_label: label of the dependent variable
    - titte: title of the plot
    - if_plt: whether to plot the regression line

    Output:
    - linear regression analysis results
    - plot of the regression line
    """
    X = merged_df[x_col]
    X = sm.add_constant(X)
    y = merged_df[y_col]

    model = sm.OLS(y, X)
    results = model.fit()
    print(results.summary())

    if if_plt:
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.regplot(data=merged_df, x=x_col, y=y_col, ax=ax)
        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.title(titte)
        plt.show()
