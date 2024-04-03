# Solar Adoption in the United States Wastewater Sector

[![CI](https://github.com/Yer1k/solar_wastewater/actions/workflows/main.yml/badge.svg)](https://github.com/Yer1k/solar_wastewater/actions/workflows/main.yml)

## Table of Contents
1. [Introduction](#Introduction)  
2. [Data Sources](#DataSources)   
   2.1 [Data Provided By Client](#ClientData)  
   2.2 [OpenStreetMap](#OSM)  
   2.3 [EPA](#EPA)  
   2.4 [HydroWaste](#HydroWaste)  
3. [Methodology](#Methodology)  
   3.1 [Overview](#MethodologyOverview)  
   3.2 [Process Diagram](#ProcessDiagram)  
5. [Experiments](#Experiments)  
   5.1 [Overview](#ExperimentOverview)  
   5.2 [Models](#Models)  
   5.3 [Metrics](#Metrics)  
6. [Results](#Results)
5. [Conclusion](#Conclusion)  
7. [Resources](#Resources)  
8. [Members](#Members)

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

<img src="40_docs/figures/client_data_map.png" width="500" height="300">

Below is a map of the possible WWTPs after mergining all datasets:

<img src="40_docs/figures/three_sources_map.png" width="600" height="300">

As can be seen from the above image, there are many WWTPs that do not overlap, indicating that none of the datasets are comprehensive.

## Methodology <a name="Methodology"></a>

### Overview <a name="MethodologyOverview"></a>

Since the number of possible WWTPs from the different sources are too many to manually verify for true WWTP and solar presence, we manually verified and tagged the possible WWTPs from all three data sources for California and Texas, as they were of primary importance to our client. We used this as the training dataset for our scene binary classification model and used the trained model to predict presence of WWTP in the images for other states. We obtained 10k WWTPs from the model inference. Once we had a verified list of all WWTPs, we manually verified the presence of solar.

### Process Diagram <a name="ProcessDiagram"></a>

<img src="40_docs/figures/methodology.png" width="600" height="300">

## Experiments <a name="Experiments"></a>
In this section, we will dive deep into our experimentation process.

### Overview <a name="ExperimentOverview"></a>

We not only needed to find the best model parameters for our training data but also test if a model trained on California and Texas would perform well for other states. We came up with two stages to our experiments.

#### Stage 1: Parameter Tuning 

#### Stage 2: Within Domain vs Cross Domain Performance

### Models <a name="Models"></a>

The model used was ResNet50. ResNet50 is a specific type of convolutional neural network. It provides the option to add more convolutional layers to a CNN, without running into the vanishing gradient problem, using the concept of shortcut connections. A shortcut connection “skips over” some layers, converting a regular network to a residual network. The 50-layer ResNet uses a bottleneck design for the building block. A bottleneck residual block uses 1×1 convolutions, known as a “bottleneck”, which reduces the number of parameters and matrix multiplications. This enables much faster training of each layer.

Below is the architecture of ResNet50:

<img src="40_docs/figures/resnet50.png" width="700" height="300">

### Metrics <a name="Metrics"></a>

1. F1 Score: The F1 score is a measure of a model's accuracy that combines the precision and recall scores. It is calculated as the harmonic mean of precision and recall. The relative contribution of precision and recall to the F1 score are equal. 
The F1 score can range from 0 to 1, with a higher score indicating better model performance.

``` math
F_{1}=\frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}
```

2. AUC: The Area Under the Curve (AUC) is the measure of the ability of a binary classifier to distinguish between classes and is used as a summary of the ROC curve.
The higher the AUC, the better the model’s performance at distinguishing between the positive and negative classes.

## Results <a name="Results"></a>

After merging all the datasets we had 40,397 possible WWTPs.

<img src="40_docs/figures/before.png" width="500" height="300">

After running model inference, we have 11,092 verified WWTPs.

<img src="40_docs/figures/after.png" width="500" height="300">

The comprehensive, verified list of WWTPs across United States can be found [here](add link).

## Conclusion <a name="Conclusion"></a>

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