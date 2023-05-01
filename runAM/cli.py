import runAM.read.json_file

def interpreter():
    """Main function of the runAM.cli module that starts the CLI interpreter and executes the specified python module.
    """
    # load CLI specification
    cli_spec = runAM.read.json_file()