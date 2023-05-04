# Load the data from CSVs and convert the processed data to AVD variables.
import runAM.csv

class _CSVtoAVD:

    def __init__(self, csv_data_directory) -> None:

        # init dictionary to build AVD port provisioning variables
        self.vars = {
            'csv': runAM.csv.read_all_from_dir(csv_data_directory),  # load data from CSV files
            'avd': dict(),  # store AVD variables
        }

    def get_vars(self):
        return self.vars
    
def CSVtoAVD(csv_data_directory):

    inst = _CSVtoAVD(csv_data_directory)
    return inst.get_vars()
