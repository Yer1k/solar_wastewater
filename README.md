# Solar Adoption in the United States Wastewater Sector

[![CI](https://github.com/Yer1k/solar_wastewater/actions/workflows/main.yml/badge.svg)](https://github.com/Yer1k/solar_wastewater/actions/workflows/main.yml)

## Table of Contents
1. [Introduction](#Introduction)  
2. [Data Sources](#DataSources)  
   3.1 [OpenStreetMap](#OSM)  
   3.2 [EPA](#EPA)  
   3.3 [HydroWaste](#HydroWaste)
3. [Methodology](#Methodology)  
4. [Experiments](#Experiments)
5. [Conclusion](#Conclusion)  
5. [Model Inference Instructions](#ModelInference)
6. [Resources](#Resources)  
7. [Members](#Members)

## Introduction <a name="Introduction"></a>
Wastewater treatment plants act as the largest energy consumers for many municipalities across the United States, requiring 30-40% of the total energy accounted for by local governments and accounting for a large portion of the operating costs at wastewater treatment plants. According to the Department of Energy, “across the country, municipal wastewater treatment plants are estimated to consume more than 30 terawatt-hours per year of electricity, which equates to about $2 billion in annual electric costs” (Department of Energy [1]). However, there are efforts to curtail this and decrease operating costs by increasing renewable energy resources at these sites, mostly in the form of solar panels. While there is great optimism about using renewable resources to make wastewater treatment plants more energy-independent, our understanding of the extent and magnitude of renewable energy adoption in these plants remains constrained due to the unavailability of an exhaustive database of wastewater treatment plants and the status of their solar energy usage. This project is conceived to bridge this critical data gap that currently exists by addressing the research question: What is the scope and scale of solar energy adoption at wastewater treatment plants (WWTPs) in the United States? The answer to this question will enable government officials and researchers, like our client Dr. Christine Kirchoff and her team, to understand energy consumption levels pre- and post-solar adoption, potential energy savings, and identifying future potential candidates for adoption of renewable resources.

To address this question, we plan to leverage and add to the existing data on wastewater treatment plants and methodologies provided by our client. This project will subsequently result in a database of WWTPs within the United States including information of WWTPs with solar adoption and those without.

## Data Sources <a name="DataSources"></a>

### OpenStreetMap (OSM) <a name="OSM"></a>

OpenStreetMap (OSM) is a free and open geographic database. It is updated and maintained by a community of volunteers. Since all geographic structures in OSM's database are tagged, we filter wastewater treatment plants using the tag "man_made"="wastewater_plant". Although the abundance and accessibility of the data are advantageous, upon closer examination, we discovered discrepancies between this data from OSM and our client's specific criteria for wastewater treatment plants (WWTPs). Despite the extensive nature of the data in OpenStreetMap (OSM), it did not fully align with our client's definition of WWTPs.

### Environmental Protection Agency (EPA) <a name="EPA"></a>

We also use a WWTP dataset published by the Environmental Protection Agency (EPA) with information relating to location and facility identification from the EPA's Facility Registry Service (FRS) from the year 2020.

### HydroWaste <a name="HydroWaste"></a>

## Methodology <a name="Methodology"></a>

## Experiments <a name="Experiments"></a>
In this section, we will dive deep into our experimentation process.

### Models <a name="Models"></a>

### Results <a name="Results"></a>

## Conclusion <a name="Conclusion"></a>

## Model Inference Instructions <a name="ModelInference"></a>

## Resources <a name="Resources"></a>
1. [Department of Energy. (n.d.). Wastewater Infrastructure. Energy.gov. Retrieved September 27, 2023](https://www.energy.gov/scep/slsc/wastewater-infrastructure#:~:text=Across%20the%20country%2C%20municipal%20wastewater,billion%20in%20annual%20electric%20costs)<a name="energy-ref"></a>

## Project Members <a name="Members"></a>
[Pooja Kabber](https://www.linkedin.com/in/poojakabber/)  
[Sukhpreet Sahota]()  
[Dingkun Yang]()  
[Yuanjing Zhu]() 

#### Project Mentors: [Dr. Kyle Bradbury](https://energy.duke.edu/about/staff/kyle-bradbury), [Dr. Christine Kirchhoff](https://iee.psu.edu/people/christine-j-kirchhoff)