# Iceberg Catalog for Analysis of Greenland Environments: ICE-AGE

## About

Freshwater flux from ice-sheet mass loss raises global sea level, influences biogeochemical systems
and fisheries, and modifies water mass properties, which can feed back into both regional and global
ocean circulation. In particular, icebergs calved from marine-terminating glaciers are critical
vectors for transporting freshwater and bioessential micronutrients at both local and remote scales.
To better enable iceberg data exploration and research activities, we have developed ICE-AGE, an
interactive web application for visualizing and extracting statistics of Greenland's Icebergs.

## Running the application

The below setup and running instructions assume you have a working installation
of the `conda` command on your local machine. The recommended way to install this
uses the [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html#)
package manager, which is
a [drop-in replacement](https://mamba.readthedocs.io/en/latest/user_guide/mamba.html)
for `conda`. All the commands used with `conda` can be executed in the same manner with `mamba`.

ICE-AGE set-up and commands shown below are executed in a terminal. There are
two parts to complete this process:

1. Setting up the conda environment and run the application
2. Importing the data using the running application

### Conda environment setup

* Clone this repository to a local path on your machine.  
  This step creates a local copy of the repository on your machine, which is
  used to run the application.
  
  ```bash
  cd /path/to/cloned/location
  git clone https://github.com/CryoGARS-Glaciology/ice-age.git
  ```
* Create the `ice_age` conda environment using the [`environment.yaml`](environment.yaml)
  file provided in the repository. This will install all the required Python packages
  and dependencies to run the application.
  
  ```bash
    cd /path/to/cloned/location/ice-age
    mamba env create -f environment.yaml 
  ```

### Downloading the required data

The required data that powers this application is not included in this repository.
To download the data, go to: TBD

### Starting the application

* Navigate to the cloned repository
  ```bash
  cd /path/to/cloned/location/ice-age
  ```
* Start the application
  ```bash
  ./start_ice_age.sh
  ```
  When the application is successfully started using the above command, a browser window
  will open automatically. The startup page of the application will have instructions for
  importing the data downloaded in the previous step. Follow these instructions to finish
  the setup.

### Stopping the application

To stop the application, simply press `CTRL + C` in the terminal where the
application is running. This will stop the Streamlit server and close the
application.

## Core Technologies

* [Streamlit](https://streamlit.io/)
* [DuckDB](https://duckdb.org/)

## History Credits

This application was first prototyped by
[Alexandra Friel](https://github.com/alexandra-friel/Greenland-icebergmeltrate-interactive)
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

ICE-AGE development and the associated research has been supported by the U.S. National Science
Foundation Office of Polar Programs (grant no. 2052549).

<img alt="NSF Logo" src="https://nsf.widen.net/content/sgngfvefhx/png/NSF_Official_logo_RGB.png?position=c&quality=80" width="100">
