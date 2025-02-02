# Load the data from CSVs and convert the processed data to AVD variables.
import runAM.csv
import sys
import glom


def ignore_error(func):
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except SystemExit as e:
            sys.exit(e)  
        except:
            pass  # ignore all other errors
    return inner_function


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
    # add various parameters to the adapter
    converter.add_description()
    converter.add_speed()
    converter.add_profile()
    converter.add_enabled_status()
    converter.add_mode()
    converter.add_mtu()
    converter.add_port_channel()
    converter.add_port_channel_short_esi()

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
        
    def get_csv(self, server_name, csv_key='', mandatory=False, unique=False):
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
                            sys.exit(f'ERROR: CSV key {csv_key} is mandatory, but the key is not defined in the CSV table!')
                        elif not csv_dict[csv_key]:
                            sys.exit(f'ERROR: CSV key {csv_key} is mandatory, but value is not defined for {server_name}!')
                    if csv_key in csv_dict.keys():
                        # only add value to the list if key is present and the value is defined and not null
                        if csv_dict[csv_key]:
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
        
    def get_adapter(self, server_name):
        # there is always just a single adapter in the list
        return self.vars['avd']['servers'][server_name]['adapters'][0]
        
    def update_adapters(self, server_name, new_dict):
        # there is always just a single adapter in the list
        self.vars['avd']['servers'][server_name]['adapters'][0].update(new_dict)

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

    @ignore_error
    def add_rack_name(self):
        # add rack name for a server if defined in CSV file
        for server_name, server_vars in self.get_avd_servers():
            rack_name = self.get_csv(server_name, csv_key='rack', unique=True)[0]
            server_vars.update({'rack': rack_name})
            self.vars['avd']['servers'].update({server_name: server_vars})

    def add_adapters(self):
        # add adapters for a server
        # adapter is a combination of following key-values: switches (mandatory), switch_ports (mandatory), endpoint_ports (if present in CSV)
        # additional adapter configuration will be added by separate functions
        for server_name, server_vars in self.get_avd_servers():
            adapter_dict = dict()  # dict to add switch_ports, switches, endpoint_ports keys 

            # TODO: add some logic here to check for conflicting use of <sw-name>:<sw-port> combination
            adapter_dict['switch_ports'] = self.get_csv(server_name, csv_key='switch_port', mandatory=True)
            adapter_dict['switches'] = self.get_csv(server_name, csv_key='switch_hostname', mandatory=True)
            try:
                adapter_dict['endpoint_ports'] = self.get_csv(server_name, csv_key='endpoint_port', mandatory=True)
            except:
                pass  # this is allowed to fail if endpoint_port is not defined in CSV

            server_vars.update({'adapters': [adapter_dict]})
            self.vars['avd']['servers'].update({server_name: server_vars})

    @ignore_error
    def add_description(self):
        # add description for existing adapters
        # adapter must exist before description can be added

        for server_name, _ in self.get_avd_servers():
            description_string = self.get_csv(server_name, csv_key='description', unique=True)[0]
            self.update_adapters(server_name, {'description': description_string})

    @ignore_error
    def add_speed(self):
        for server_name, _ in self.get_avd_servers():
            speed_string = self.get_csv(server_name, csv_key='speed', unique=True)[0]
            self.update_adapters(server_name, {'speed': speed_string})

    @ignore_error
    def add_profile(self):
        for server_name, _ in self.get_avd_servers():
            profile_string = self.get_csv(server_name, csv_key='profile', unique=True)[0]
            self.update_adapters(server_name, {'profile': profile_string})

    @ignore_error
    def add_enabled_status(self):
        for server_name, _ in self.get_avd_servers():
            enable_string = self.get_csv(server_name, csv_key='enabled', unique=True)[0]
            if enable_string.lower() == "true":
                enable_bool = True
            elif enable_string.lower() == "false":
                enable_bool = False
            else:
                sys.exit(f'ERROR: "enabled" key must be set to "true" or "false", but it is set to "{enable_string}" for the {server_name}!')
            self.update_adapters(server_name, {'enabled': enable_bool})

    @ignore_error
    def add_mode(self):
        for server_name, _ in self.get_avd_servers():
            mode_string = self.get_csv(server_name, csv_key='mode', unique=True)[0]
            if mode_string.lower() not in ['access', 'dot1q-tunnel', 'trunk']:
                sys.exit(f'ERROR: "mode" key must be set to "access", "dot1q-tunnel" or "trunk", but it is set to "{mode_string}" for the {server_name}!')
            self.update_adapters(server_name, {'mode': mode_string.lower()})

    @ignore_error
    def add_mtu(self):
        for server_name, _ in self.get_avd_servers():
            mode_string = self.get_csv(server_name, csv_key='mtu', unique=True)[0]
            try:
                mtu = int(mode_string)
            except:
                sys.exit(f'ERROR: can not convert MTU "{mode_string}" to integer for {server_name}!')
            else:
                if 1 <= mtu <= 9216:
                    self.update_adapters(server_name, {'mtu': mode_string.lower()})
                else:
                    sys.exit(f'ERROR: MTU must be between 1 and 9216. It is set to {mtu} for {server_name}! ')

    def add_port_channel(self):
        for server_name, _ in self.get_avd_servers():
            port_channel_mode_string = self.get_csv(server_name, csv_key='port_channel.mode', unique=True)[0]
            if port_channel_mode_string.lower() in ['active', 'passive', 'on']:
                self.update_adapters(server_name, {'port_channel': {
                    'mode': port_channel_mode_string.lower()
                }})

    def add_port_channel_short_esi(self):
        for server_name, _ in self.get_avd_servers():
            port_channel_short_esi_string = self.get_csv(server_name, csv_key='port_channel.short_esi', unique=True)[0]
            if port_channel_short_esi_string.lower() == 'auto':
                pass  # if short esi is set to auto - it's a valid value
            else:
                for hex in port_channel_short_esi_string.split(':'):
                    try:
                        int(hex, 16)
                    except Exception as _:
                        sys.exit(f'ERROR: short_esi must be hex or "auto", but it is set to {port_channel_short_esi_string} for {server_name}!')
            # if no error detected, set short esi
            adapter = self.get_adapter(server_name)
            if 'port_channel' not in adapter.keys():
                sys.exit(f'ERROR: port_channel.mode must be defined before defining short_esi for {server_name}!')
            adapter['port_channel'].update({'short_esi': port_channel_short_esi_string})
            self.update_adapters(server_name, adapter)
