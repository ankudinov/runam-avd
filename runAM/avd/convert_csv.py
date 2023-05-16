# Load the data from CSVs and convert the processed data to AVD variables.
import runAM.csv
import sys
import glom


class GlomDict(dict):

    def assign(self, glom_path, value):
        glom.assign(self, glom_path, value, missing=dict)

    def glom(self, glom_spec):
        return glom.glom(self, glom_spec)


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
        self.vars = GlomDict({
            'csv': runAM.csv.read_all_from_dir(csv_data_directory),  # load data from CSV files
            'avd': dict(),  # store AVD variables
        })

    def get_csv_server_names(self):
        unique_csv_server_names = set([ csv_server['server_name'] for csv_server in self.vars['csv']['servers'] ])
        return list(unique_csv_server_names)
        
    def get_csv_by_server_name(self, server_name, csv_key='', mandatory=False, unique=False):
        # get CSV values for specific server
        # if csv_key is not defined, a list of dictionaries with all values will be returned
        # if csv_key is defined, the list of values for this key and specific server will be returned
        # if mandatory is True, the key must be defined in the CSV
        # if unique is True, the value must be the same for all key occurrences for the specific server
        if csv_key:
            csv_value_list = list()
            for csv_dict in self.vars['csv']['servers']:
                if csv_dict['server_name'] == server_name:
                    if mandatory:
                        if csv_key not in csv_dict.keys():
                            sys.exit(f'ERROR: CSV key {csv_key} is mandatory, but not defined for {server_name}!')
                        else:
                            csv_value_list.append(csv_dict[csv_key])
            if unique:
                if len(set(csv_value_list)) > 1:
                    sys.exit(f'ERROR: different {csv_key} CSV values were defined for {server_name}. {csv_key} must be unique!')
            return csv_value_list
        else:
            return [ csv_dict for csv_dict in self.vars['csv']['servers'] if csv_dict['server_name'] == server_name ]

    def get_avd_servers(self, csv_filtered=True):
        # if filtered is True only the servers to be updated will be returned
        avd_servers = dict()
        for k, v in self.vars['avd']['servers'].items():
            if csv_filtered and k not in self.get_csv_server_names():
                pass  # skip if server was loaded from AVD variables and not defined in CSVs
            else:
                avd_servers.update({k:v})
        return avd_servers.items()

    def get_avd_vars_by_server_name(self, server_name):
        if server_name not in self.vars['avd']['servers'].keys():
            sys.exit(f'ERROR: server {server_name} is not present in AVD vars!')
        else:
            return self.vars['avd']['servers'][server_name]

    def add_servers_names(self):
        # add { server_name: { 'adapters': [] } } dictionary for a new server
        if 'servers' not in self.vars['avd'].keys():
            self.vars['avd']['servers'] = dict()  # add 'servers' keys if no existing AVD servers were loaded
        for csv_server_name in self.get_csv_server_names():
            if csv_server_name in self.vars['avd']['servers'].keys():
                sys.exit(f'ERROR: server {csv_server_name} is already present in AVD vars and must be deleted before it can be updated!')
            else:
                self.vars['avd']['servers'].update({
                    csv_server_name: { 'adapters': list() }
                })

    def add_rack_name(self):
        # add rack name for a server if defined in CSV file
        for server_name, server_vars in self.get_avd_servers():
            rack_name_set = set([ csv['rack'] for csv in self.get_csv_by_server_name(server_name) ])
            if len(rack_name_set) > 1:
                # error if rack name was added on the previous iteration and is not the same in CSV entries
                sys.exit(f'ERROR: different rack names specified for the same server ID {server_name}')
            else:
                server_vars.update({'rack': list(rack_name_set)[0]})
                self.vars['avd']['servers'].update({server_name: server_vars})

    def add_adapters(self):
        # add adapters for a server
        # adapter is a combination of following key-values: switches (mandatory), switch_ports (mandatory), endpoint_ports (if present in CSV)
        # additional adapter configuration will be added by separate functions
        for server_name, server_vars in self.get_avd_servers():
            adapter_dict = {
                'switches': list(),
                'switch_ports': list(),
                'endpoint_ports': list()
            }
            for csv_entry in self.get_csv_by_server_name(server_name):
                # TODO: add some logic here to check for conflicting use of <sw-name>:<sw-port> combination
                if 'switch_port' in csv_entry.keys():
                    if csv_entry['switch_port']:
                        adapter_dict['switch_ports'].append(csv_entry['switch_port'])
                    else:
                        sys.exit(f'ERROR: switch_port is a mandatory field and can not be empty for {server_name}')
                else:
                    sys.exit('ERROR: switch_port is a mandatory field and must be defined in the CSV file.')

                if 'switch_hostname' in csv_entry.keys():
                    if csv_entry['switch_hostname']:
                        adapter_dict['switches'].append(csv_entry['switch_hostname'])
                    else:
                        sys.exit(f'ERROR: switch_hostname is a mandatory field and can not be empty for {server_name}')
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
                    sys.exit(f'ERROR: endpoint_ports length is different from switches length for {server_name}')

            server_vars.update({'adapters': [adapter_dict]})
            self.vars['avd']['servers'].update({server_name: server_vars})


    def add_description(self):
        # add description for existing adapters
        # adapter must exist before description can be added
        for server_name, server_vars in self.get_avd_servers():
            description_set = set([ csv['description'] for csv in self.get_csv_by_server_name(server_name) ])
            if len(description_set) > 1:
                sys.exit(f'ERROR: same description must be configured for all CSV entries corresponding to a single adapter. Verify {server_name} settings.')
            else:
                server_vars['adapters'][0].update({'description': list(description_set)[0]})
                self.vars['avd']['servers'].update({server_name: server_vars})
