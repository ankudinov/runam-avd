import os
import sys

def file_in_dir_and_subdirs(dirname, target_filename):
    """Find file in the specified directory and all subdirectories.

    Args:
        dirname (str): Directory name to start search
        target_filename (str): Target filename

    Returns:
        list: Full path list matching the specified file name.
    """
    filename_list = list()
    for dirpath, _, filenames in os.walk(dirname):
        for filename in [f for f in filenames if f == target_filename]:
            filename_list.append(
                os.path.abspath(os.path.join(dirpath, filename))
            )

    return filename_list


def file_full_path(filename, dirname = '', single_match = True):
    """This function takes a short filename and optional prefix and returns full path.

    Args:
        filename (str): The filename to search and return it's full path
        dirname (str, optional): The directory name to search for a file. Defaults to ''.
            By default the file search will start in the current working directory.
        single_match (bool, optional): If true, returns as single filename, otherwise list of matching files. Defaults to True.

    Returns:
        list: Full path list matching the specified filename. By default must be a single full path.
    """

    if dirname:
        search_directory = dirname
    else:
        search_directory = os.getcwd()

    full_path_list = file_in_dir_and_subdirs(search_directory, filename)


    if len(full_path_list) == 0:
        sys.exit(f'ERROR: can not find "{filename}" in {search_directory}')
    if single_match and len(full_path_list) > 1:
            sys.exit(f'ERROR: single_math flag is True, but multiple there are multiple files in {search_directory} matching  "{filename}"')
    
    return full_path_list
