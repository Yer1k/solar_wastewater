# Solar Adoption in the United States Wastewater Sector

[![CI](https://github.com/Yer1k/solar_wastewater/actions/workflows/main.yml/badge.svg)](https://github.com/Yer1k/solar_wastewater/actions/workflows/main.yml)

## Table of Contents
1. [Introduction](#Introduction)  
2. [Data Sources](#DataSources)  
   3.1 [Data Provided By Client](#ClientData)
   3.2 [OpenStreetMap](#OSM)  
   3.3 [EPA](#EPA)  
   3.4 [HydroWaste](#HydroWaste)
3. [Methodology](#Methodology)  
4. [Experiments](#Experiments)
5. [Conclusion](#Conclusion)  
5. [Model Inference Instructions](#ModelInference)
6. [Resources](#Resources)  
7. [Members](#Members)

## Introduction <a name="Introduction"></a>
Wastewater treatment plants act as the largest energy consumers for many municipalities across the United States, requiring 30-40% of the total energy accounted for by local governments and accounting for a large portion of the operating costs at wastewater treatment plants. According to the Department of Energy, “across the country, municipal wastewater treatment plants are estimated to consume more than 30 terawatt-hours per year of electricity, which equates to about $2 billion in annual electric costs” (Department of Energy [1]). However, there are efforts to curtail this and decrease operating costs by increasing renewable energy resources at these sites, mostly in the form of solar panels. While there is great optimism about using renewable resources to make wastewater treatment plants more energy-independent, our understanding of the extent and magnitude of current solar energy adoption in these plants remains constrained due to the unavailability of an exhaustive database of wastewater treatment plants and the status of their solar energy usage. This project is conceived to bridge this critical data gap that currently exists by addressing the research question: What is the scope and scale of solar energy adoption at wastewater treatment plants (WWTPs) in the United States, in particular within California and Texas? The answer to this question will enable government officials and researchers, like our client Dr. Christine Kirchoff and her team, to understand energy consumption levels pre- and post-solar adoption, potential energy savings, and identifying future potential candidates for adoption of solar energy.

To address this question, we plan to leverage and add to the existing data on wastewater treatment plants provided by our client. This project will subsequently result in a database of WWTPs within the United States including information of WWTPs with solar adoption and those without.

## Data Sources <a name="DataSources"></a>

### Data Provided by Client <a name="ClientData"></a>

The data provided by our client consisted of 40 WWTPs in California that were manually verified. The data can be found [here](Add link to drive).

### OpenStreetMap (OSM) <a name="OSM"></a>

OpenStreetMap (OSM) is a free and open geographic database. It is updated and maintained by a community of volunteers. Since all geographic structures in OSM's database are tagged, we filter wastewater treatment plants using the tag "man_made"="wastewater_plant". This resulted in 14,282 possible WWTPs. Although the abundance and accessibility of the data are advantageous, upon closer examination, we discovered discrepancies between this data from OSM and our client's specific criteria for wastewater treatment plants (WWTPs). Despite the extensive nature of the data in OpenStreetMap (OSM), it did not fully align with our client's definition of WWTPs. More information can be found [here](#osm-ref).

### Environmental Protection Agency (EPA) <a name="EPA"></a>

We also use a WWTP dataset published by the Environmental Protection Agency (EPA) with information relating to location and facility identification from the EPA's Facility Registry Service (FRS) from the year 2020. The size of this dataset was 14,327 possible WWTPs. Similar to OSM, after analysing the data, we found that there were entries tagged as wastewater treatment plants but were ponds or other geographic structures like forests.

### HydroWaste <a name="HydroWaste"></a>

An open-source spatially explicit global database of 58,502 wastewater treatment plants (WWTPs)​ and various other characteristics such as population served, amount of wastewater discharged, dilution factor of nearby water bodies that wastewater is discharged into, etc. After filtering for United States, this resulted in 14,748 possible WWTPs. Similar to the OSM and EPA datasets, after analysing the data, we found that there were entries tagged as wastewater treatment plants but were not. More information can be found [here](#hydrowaste-ref).

Below is an example of images that demonstrate the incorrect tagging from the above three data sources:

True WWTP

<img src="40_docs/figures/wwtp_example.png" width="600" height="400">

Falsely Labeled as WWTP

<img src="40_docs/figures/not_wwtp_example.png" width="600" height="400">

After merging the four datasets, we had 40,397 possible WWTPs.

Below is a map of the WWTPs with solar provided by the client:

<img src="40_docs/figures/client_data_map.png" width="800" height="600">

Below is a map of the possible WWTPs after mergining all datasets:

<img src="40_docs/figures/three_sources_map.png" width="800" height="600">

As can be seen from the above image, there are many WWTPs that do not overlap, indicating that none of the datasets are comprehensive.

## Methodology <a name="Methodology"></a>

Overview

Since the number of possible WWTPs from the different sources are too many to manually verify for true WWTP and solar presence, we manually verified and tagged the possible WWTPs from all three data sources for California and Texas, as they were of primary importance to our client. We used this as the training dataset for our scene binary classification model and used the trained model to predict presence of WWTP in the images for other states. We obtained 10k WWTPs from the model inference. Once we had a verified list of all WWTPs, we manually verified the presence of solar.

Process Diagram

<img src="40_docs/figures/methodology.png" width="800" height="600">

## Experiments <a name="Experiments"></a>
In this section, we will dive deep into our experimentation process.

### Models <a name="Models"></a>

### Results <a name="Results"></a>

## Conclusion <a name="Conclusion"></a>

## Model Inference Instructions <a name="ModelInference"></a>

## Resources <a name="Resources"></a>
1. [Department of Energy. (n.d.). Wastewater Infrastructure. Energy.gov. Retrieved September 27, 2023](https://www.energy.gov/scep/slsc/wastewater-infrastructure#:~:text=Across%20the%20country%2C%20municipal%20wastewater,billion%20in%20annual%20electric%20costs)<a name="energy-ref"></a>
2. [Hydrowaste](https://www.hydrosheds.org/products/hydrowaste)<a name="hydrowaste-ref"></a>
3. [OSM](https://www.openstreetmap.org/)<a name="osm-ref"></a>

## Project Members <a name="Members"></a>
[Pooja Kabber](https://www.linkedin.com/in/poojakabber/)  
[Sukhpreet Sahota]()  
[Dingkun Yang]()  
[Yuanjing Zhu]() 

#### Project Mentors: [Dr. Kyle Bradbury](https://energy.duke.edu/about/staff/kyle-bradbury), [Dr. Christine Kirchhoff](https://iee.psu.edu/people/christine-j-kirchhoff)