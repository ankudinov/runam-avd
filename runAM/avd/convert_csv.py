# Load the data from CSVs and convert the processed data to AVD variables.
import runAM.csv
import sys


def to_avd_yaml(csv_data_directory):

    converter = CSVtoAVDConverter(csv_data_directory)

    # add your custom logic here
    # the process of building AVD vars is suboptimal from the performance perspective
    # bu allows adding and deleting logic blocks in a simple way

    # 1. add server names to the AVD vars
    #    this method only allows to add new servers
    #    and will stop the script with error if existing server is updated without being deleted first
    #    WARNING: never remove this method from the logic, as it creates the server dictionary
    converter.add_servers_names()
    # add rack names if present
    converter.add_rack_name()
    # add adapters
    converter.add_adapters()
    # add description to adapters
    converter.add_description()

    return converter.vars


class CSVtoAVDConverter:

    def __init__(self, csv_data_directory) -> None:

        # init dictionary to build AVD port provisioning variables
        self.vars = {
            'csv': runAM.csv.read_all_from_dir(csv_data_directory),  # load data from CSV files
            'avd': dict(),  # store AVD variables
        }

    def add_servers_names(self):
        # add { server_name: { 'adapters': [] } } dictionary for a new server
        new_server_names_list = list()
        for csv_server in self.vars['csv']['servers']:
            if 'servers' not in self.vars['avd'].keys():
                self.vars['avd'].update({'servers': dict()})
            if csv_server['server_name'] in new_server_names_list:
                pass  # if server name was added on the previous iteration, do nothing
            elif csv_server['server_name'] in self.vars['avd']['servers'].keys():
                sys.exit(f'ERROR: server {csv_server["server_name"]} is already present in AVD vars and must be deleted before it can be updated!')
            else:
                new_server_names_list.append(csv_server['server_name'])
                self.vars['avd']['servers'].update({
                    csv_server['server_name']: {
                        'adapters': list()
                    }
                })

    def add_rack_name(self):
        # add rack name for a server if defined in CSV file
        for csv_server in self.vars['csv']['servers']:
            avd_server = self.vars['avd']['servers'][csv_server['server_name']]
            if 'rack' in avd_server.keys():
                if avd_server['rack'] != csv_server['rack']:
                    # error if rack name was added on the previous iteration and is not the same in CSV entries
                    sys.exit(f'ERROR: different rack names specified for the same server ID {csv_server["server_name"]}')
            elif 'rack' in csv_server.keys():
                avd_server.update({'rack': csv_server['rack']})

    def add_adapters(self):
        # add adapters for a server
        # adapter is a combination of following key-values: switches (mandatory), switch_ports (mandatory), endpoint_ports (if present in CSV)
        # additional adapter configuration will be added by separate functions
        for avd_server_name in self.vars['avd']['servers'].keys():
            avd_server = self.vars['avd']['servers'][avd_server_name]
            csv_entry_list = [ csv_entry for csv_entry in self.vars['csv']['servers'] if csv_entry['server_name'] == avd_server_name]
            switch_ports_list = list()
            switches_list = list()
            endpoint_ports_list = list()
            for csv_entry in csv_entry_list:
                # TODO: add some logic here to check for conflicting use of <sw-name>:<sw-port> combination
                if 'switch_port' in csv_entry.keys():
                    if csv_entry['switch_port']:
                        switch_ports_list.append(csv_entry['switch_port'])
                    else:
                        sys.exit(f'ERROR: switch_port is a mandatory field and can not be empty for {avd_server_name}')
                else:
                    sys.exit('ERROR: switch_port is a mandatory field and must be defined in the CSV file.')
                if 'switch_hostname' in csv_entry.keys():
                    if csv_entry['switch_hostname']:
                        switches_list.append(csv_entry['switch_hostname'])
                    else:
                        sys.exit(f'ERROR: switch_hostname is a mandatory field and can not be empty for {avd_server_name}')
                else:
                    sys.exit('ERROR: switch_hostname is a mandatory field and must be defined in the CSV file.')
                if 'endpoint_port' in csv_entry.keys():
                    endpoint_ports_list.append(csv_entry['endpoint_port'])
            avd_server.update({
                'adapters': [
                    {
                        'switches': switches_list,
                        'switch_ports': switch_ports_list,
                        'endpoint_ports': endpoint_ports_list
                    }
                ]
            })

    def add_description():
        # add description for existing adapters
        pass
