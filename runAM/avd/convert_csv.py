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
            adapter_dict = {
                'switches': list(),
                'switch_ports': list(),
                'endpoint_ports': list()
            }
            for csv_entry in csv_entry_list:
                # TODO: add some logic here to check for conflicting use of <sw-name>:<sw-port> combination
                if 'switch_port' in csv_entry.keys():
                    if csv_entry['switch_port']:
                        adapter_dict['switch_ports'].append(csv_entry['switch_port'])
                    else:
                        sys.exit(f'ERROR: switch_port is a mandatory field and can not be empty for {avd_server_name}')
                else:
                    sys.exit('ERROR: switch_port is a mandatory field and must be defined in the CSV file.')
                if 'switch_hostname' in csv_entry.keys():
                    if csv_entry['switch_hostname']:
                        adapter_dict['switches'].append(csv_entry['switch_hostname'])
                    else:
                        sys.exit(f'ERROR: switch_hostname is a mandatory field and can not be empty for {avd_server_name}')
                else:
                    sys.exit('ERROR: switch_hostname is a mandatory field and must be defined in the CSV file.')
                if 'endpoint_port' in csv_entry.keys():
                    if csv_entry['endpoint_port']:
                        adapter_dict['endpoint_ports'].append(csv_entry['endpoint_port'])
            # check if endpoint_ports was defined, remove if not as it's optional
            if len(adapter_dict['endpoint_ports']) == 0:
                del adapter_dict['endpoint_ports']
            else:
                # if endpoint_ports was defined it must have the same length as switches
                if len(adapter_dict['endpoint_ports']) != len(adapter_dict['switches']):
                    sys.exit(f'ERROR: endpoint_ports length is different from switches length for {avd_server_name}')
            avd_server['adapters'].append(adapter_dict)


    def add_description(self):
        # add description for existing adapters
        # adapter must exist before description can be added
        for avd_server_name in self.vars['avd']['servers'].keys():
            avd_server = self.vars['avd']['servers'][avd_server_name]
            csv_entry_list = [ csv_entry for csv_entry in self.vars['csv']['servers'] if csv_entry['server_name'] == avd_server_name]
            # verify that description is the same for an adapter
            description_string = ''
            for csv_entry in csv_entry_list:
                if not description_string:
                    description_string = csv_entry['description']
                elif description_string != csv_entry['description']:
                    sys.exit(f'ERROR: same description must be configured for all CSV entries corresponding to a single adapter. Verify {avd_server_name} settings.')
            # update description
            # there should be a single adapter, but we'll walk the list to keep it universal
            for adapter in avd_server['adapters']:
                adapter['description'] = description_string
