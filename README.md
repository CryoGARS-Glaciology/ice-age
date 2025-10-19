# Iceberg Catalog for Analysis of Greenland Environments: ICE-AGE

## About
Interactive web application for visualizing and extracting statistics from
Greenland's Icebergs.

## Running the application
The below setup and running instructions assume you have a working installation
of the `conda` command on your local machine. The recommended way to install this
uses the [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html#)
package manager, which is a [drop-in replacement](https://mamba.readthedocs.io/en/latest/user_guide/mamba.html) 
for `conda`. All the commands used with `conda` can be executed the same manner with `mamba`.

All set up and running commands below are executed in a terminal.

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
* Twila A. Moon[^1] (Project PI)
* Dustin Carroll[^2]
* Ellyn Enderlin[^3]
* Aman KC[^3]
* Alexandra Friel[^3]
* Joachim Meyer[^4]

Affiliations:
[^1]: University of Colorado Boulder
[^2]: San Jose State University
[^3]: Boise State University
[^4]: SciTenia LLC