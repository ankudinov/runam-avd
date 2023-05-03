import sys
import runAM.tools.find
import csv
import os


def read(csv_file_name):
    try:
        csv_row_dict_list = list()  # list of key-value pairs produced from every CSV row except header
        with open(runAM.tools.find.file_full_path(csv_file_name)[0], mode='r') as csv_file:
            # if header contains __CCvar and __CCvalue CSV will be processed vertically
            # each row will be treated as separate variable with a name of __CCvar
            vars_from_csv = dict()
            for row in csv.DictReader(csv_file):
                updated_row_dict = dict()
                for k, v in row.items():
                    # remove potential spaces left and right
                    k = k.strip()
                    if v:
                        v = v.strip()
                    updated_row_dict.update({k: v})
                if '__CCkey' in updated_row_dict.keys():
                    if not '__CCvalue' in updated_row_dict.keys():
                        sys.exit(
                            f'ERROR: __CCkey is defined without __CCvalue in {csv_file}')
                    vars_from_csv.update({updated_row_dict['__CCkey']: updated_row_dict['__CCvalue']})
                else:
                    csv_row_dict_list.append(updated_row_dict)

        if len(csv_row_dict_list):
            return csv_row_dict_list
        else:
            return vars_from_csv
    except Exception as e:
        sys.exit(f'ERROR: Can not load the CSV file {csv_file_name} due to following error:\n{e}')


def read_all_from_dir(csv_data_directory):

    data_loaded_from_csvs = dict()

    # build full path list of all files ending with .csv
    csv_file_list = runAM.tools.find.file_full_path('\.csv$', csv_data_directory, single_match=False, regex=True)
    # load data
    for a_file in csv_file_list:
        csv_data = read(a_file)
        csv_basename = os.path.basename(a_file)
        data_loaded_from_csvs.update({
            # [:-4] removes .csv
            csv_basename.lower()[:-4]: csv_data
            })
        
    return data_loaded_from_csvs
