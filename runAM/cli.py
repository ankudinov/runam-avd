import runAM.json

def interpreter():
    """Main function of the runAM.cli module that starts the CLI interpreter and executes the specified python module.
    """
    # load CLI specification
    cli_spec = runAM.json.read('cli_spec.json')
