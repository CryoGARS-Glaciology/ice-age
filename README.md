# Iceberg Catalog for Analysis of Greenland Environments: ICE-AGE

## About

Freshwater flux from ice-sheet mass loss raises global sea level, influences biogeochemical systems and fisheries, 
and modifies water mass properties, which can feedback into both regional and global ocean circulation. 
In particular, icebergs calved from marine-terminating glaciers are critical vectors for transporting freshwater and bioessential 
micronutrients at both local and remote scales. To better enable iceberg data exploration and research activities, we have developed 
ICE-AGE, an interactive web application for visualizing and extracting statistics of Greenland's Icebergs. Instructions for running
ICE-AGE are provided below.

## Running the application
The below setup and running instructions assume you have a working installation
of the `conda` command on your local machine. The recommended way to install this
uses the [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html#)
package manager, which is a [drop-in replacement](https://mamba.readthedocs.io/en/latest/user_guide/mamba.html) 
for `conda`. All the commands used with `conda` can be executed the same manner with `mamba`.

ICE-AGE set-up and commands shown below are executed in a terminal.

### Conda environment setup
* Clone this repository to a local path on your machine
  ```bash
  cd /path/to/cloned/location
  git clone https://github.com/CryoGARS-Glaciology/ice-age.git
  ```
* Create the `ice_age` conda environment
  ```bash
  cd /path/to/cloned/location/ice-age
  mamba env create -f environment.yml 
  ```

### Downloading the required data
The required data that powers this application is not included in this repository.
To download the data, go to: TBD

After downloading the and extracting the data and move the content to the root of the cloned 
repository with the name `catalog-data`.
```bash
cd /path/to/dowloaded/data/
mv catalog-data /path/to/cloned/location/ice-age/
```

### Starting the application
In a terminal
* Activate the conda environment
  ```bash
  conda activate ice_age
  ```
* Navigate to the cloned repository
  ```bash
  cd /path/to/cloned/location/ice-age
  ```
* Start the app
  ```bash
  streamlit run ice_age_app.py
  ```
## Core Technologies
* [Streamlit](https://streamlit.io/)
* [DuckDB](https://duckdb.org/)

## History Credits
This app was first prototyped by [Alexandra Friel](https://github.com/alexandra-friel/Greenland-icebergmeltrate-interactive)
and development continued in this repository.

## Development Team
* Ellyn Enderlin[^1] (Project PI)
* Twila A. Moon[^2] 
* Dustin Carroll[^3][^4]
* Aman KC[^1]
* Alexandra Friel[^1]
* Joachim Meyer[^5]

Affiliations:
[^1]: Boise State University
[^2]: University of Colorado Boulder
[^3]: Moss Landing Marine Laboratories, San Josê State University
[^4]: Jet Propulsion Laboratory, California Institute of Technology
[^5]: SciTenia LLC

## Funding
ICE-AGE development and the associated research has been supported by the U.S. National Science Foundation Office of Polar Programs (grant no. 2052549).

<img src="https://previews.us-east-1.widencdn.net/preview/39958271/assets/asset-view/ee386c26-c5fb-419d-8f7b-bed1a1e84e60/thumbnail/eyJ3Ijo2MDAsImgiOjYwMCwic2NvcGUiOiJhcHAifQ==?sig.ver=1&sig.keyId=us-east-1.20240821&sig.expires=1765476000&sig=KA2usUx_6ebvhjVYw60Wbl-yAzp2yd0AeSWOSyhs44A" width="100">

