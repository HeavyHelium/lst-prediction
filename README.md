# lst-prediction
LST prediction based on remote-sensing and socio-economic factors 

## Initialization & Setting 

* Install dependencies 

```sh 
pip install -r requirements.txt
```

* Make sure you have **jupyter notebook** in some shape or form 

## Retrieval of Remote Sensing Imagery 
The data used is **selected** with a Google Earth Engine **JS** script which can be found [here](./data-collection/find-images.js). The imagery of choice is from different time periods, which contributes to the overall variability.    

It should be noted that only images with cloud coverage of less than 10% have been picked, which is efficiently carried out on the Google Earth Engine Server. 

Landsat Collection 2 served as the main source of data for this experiment. The choice of this image collection product was based on the following factors: 
* Atmopheric correction has already been performed 
* It is well documented 
* Includes a Surface Temperature product 
* Wide temporal availability - imagery has been preprocessed for the Landsat 4/5/7/8/9 satellite generations
* High resolution - least precision is 120m pixel size
* Accessible for free from USGS Earth Explorer or Google Earth Engine


Spatially, **the area of interest** is **Sofia City** Municipality. A geotif of the boundaries can be found [here](./shapefiles/sofia-boundaries.json).   

[Further retrieval](./lst-and-indices-retrieval.ipynb) is perfomed using the Google Earth Engine **Python API** in the following manner: 
*  Landsat Collection 2 is used to extract Land Surface Temperature and Spectral indices for each selected image
    * Satellites used are Landsat 5, 7, 8
* [The Global Human Settlement Layer Population dataset](https://human-settlement.emergency.copernicus.eu/ghs_pop2023.php) is utilized for the extraction of population count per pixel as a socioeconomic factor affecting Land Surface Temperature.  

All imagery has been resampled to the least precise resolution of *120m*. 

Data can be explored in the [population notebook](population-eda.ipynb) and the [remote sensing demo notebook](demo.ipynb). 

### [Pythonic Workflow](lst-and-indices-retrieval.ipynb) 

1. Collection and preprocessing
*   ```eemont``` module
    * To perform the respective cloud masking and scaling of satellite imagery 
    * To extract spectral indices in an automatic way 

2. Data handling
* ```rasterio``` for raster data handing 
    * clipping and visualization 
    * conversion to numpy arrays for dataset formation
* ```geopandas``` for vector data handling 
* ```raster_stasts``` to get zonal statistics for Sofia Municipality  

3. Machine Learning Experiment 

* ```sklearn``` for model training and validation 
