# runam-avd

A collection of Python modules to extend Ansible AVD collection

To install the runAM modules, run the following command:

```bash
pip install git+https://github.com/ankudinov/runam-avd.git
# enable argcomplete
eval "$(register-python-argcomplete runAM)"
```

Tests:

```bash
python3 -m runAM avd.convert_csv.to_avd_yaml -dir ./test/CSVs/
runAM avd.convert_csv.to_avd_yaml -dir ./test/CSVs/
```
