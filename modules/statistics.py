import pandas as pd

from modules.data_path import MELT_RATES_DIR

def load_site_names():
    site_names = []

    for site in MELT_RATES_DIR.iterdir():
        if site.is_dir():
            site_names.append(site.name)

    return site_names

def load_dates(site_name):
    folder_path = MELT_RATES_DIR.joinpath(site_name)
    dates = []

    for file in folder_path.iterdir():
        if file.suffix == ".csv":
            date = file.stem.split("_")[1]
            dates.append(date)

    return dates


def load_statistics(site_name, dates):
    folder_path = MELT_RATES_DIR.joinpath(site_name)
    for file in folder_path.iterdir():
        if dates in file.stem:
            csv_file = file
        break

    raw_csv = pd.read_csv(csv_file)

    # Drop unwanted columns
    unwanted_columns = [
        'X_i', 'Y_i', 'TimeSeparation', 'VerticalAdjustment_i', 'VerticalAdjustment_f', 'Density_i', 'Density_f'
    ]
    figure_data = raw_csv.drop(
        columns=[col for col in unwanted_columns if col in raw_csv.columns]
    )

    return raw_csv, figure_data
