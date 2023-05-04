# Load the data from CSVs and convert the processed data to AVD variables.
import runAM.csv
import sys


def to_avd_yaml(csv_data_directory):

    converter = CSVtoAVDConverter(csv_data_directory)

    # add your custom logic here
    # the process of building AVD vars is suboptimal from the performance perspective
    # bu allows adding and deleting logic blocks in a simple way

    # 1. add server names to the AVD vars
    converter.add_servers_names()

    return converter.vars


class CSVtoAVDConverter:

    def __init__(self, csv_data_directory) -> None:

        # init dictionary to build AVD port provisioning variables
        self.vars = {
            'csv': runAM.csv.read_all_from_dir(csv_data_directory),  # load data from CSV files
            'avd': dict(),  # store AVD variables
        }

    def add_servers_names(self):
        new_server_names_list = list()
        for server in self.vars['csv']['servers']:
            if 'servers' not in self.vars['avd'].keys():
                self.vars['avd'].update({'servers': dict()})
            if server['server_name'] in new_server_names_list:
                pass  # if server name was added on the previous iteration, do nothing
            elif server['server_name'] in self.vars['avd']['servers'].keys():
                sys.exit(f'ERROR: server {server["server_name"]} is already present in AVD vars and must be deleted before it can be updated!')
            else:
                new_server_names_list.append(server['server_name'])
                self.vars['avd']['servers'].update({server['server_name']: dict()})
