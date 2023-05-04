# Load the data from CSVs and convert the processed data to AVD variables.
import runAM.csv


def to_avd_yaml(csv_data_directory):

    converter = CSVtoAVDConverter(csv_data_directory)
    return converter.vars


class CSVtoAVDConverter:

    def __init__(self, csv_data_directory) -> None:

        # init dictionary to build AVD port provisioning variables
        self.vars = {
            'csv': runAM.csv.read_all_from_dir(csv_data_directory),  # load data from CSV files
            'avd': dict(),  # store AVD variables
        }
