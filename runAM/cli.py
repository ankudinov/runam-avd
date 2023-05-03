import runAM.json
import argparse
import argcomplete
import inspect
import sys
import json


def interpreter():
    """Main function of the runAM.cli module that starts the CLI interpreter and executes the specified python module.
    """
    # load CLI specification
    cli_spec = runAM.json.read('cli_spec.json')

    # process user input and execute a module
    args = runAM.cli.parse(cli_spec)
    python_module_name = cli_spec[args['subparser_name']]['python_module']
    out_data = runAM.cli.run_module(python_module_name, args)
    out_data = runAM.cli.run_module(python_module_name, args)
    if 'echo' in args.keys():
        if args['echo']:
            if isinstance(out_data, dict) or isinstance(out_data, list):
                print(json.dumps(out_data, indent=4))
            else:
                print(out_data)  # TODO: consider logging


def add_arguments(a_parser, argument_list):
    """Add arguments to a parser

    Args:
        a_parser (argparse parser object): a parser to modify
        argument_list (list): list of augment specification dictionaries
    """

    for an_argument in argument_list:

        args = [
            an_argument['arg_name'],
            an_argument['arg_short_name'],
        ]

        kwargs = {'help': an_argument['help']}
        if 'action' in an_argument.keys():
            kwargs.update({'action': an_argument['action']})
        if 'default' in an_argument.keys():
            kwargs.update({'default': an_argument['default']})
        if 'choices' in an_argument.keys():
            kwargs.update({'choices': an_argument['choices']})
        if 'type' in an_argument.keys():
            kwargs.update({'type': eval(an_argument['type'])})  # eval to convert string to type
        if 'required' in an_argument.keys():
            kwargs.update({'required': an_argument['required']})

        a_parser.add_argument(*args, **kwargs)


def run_module(module_name_string, args_dict):
    """Run a module specified via CLI.

    Args:
        module_name_string (str): Module name to execute.
        args_dict (dict): CLI arguments dictionary.

    Returns:
        [any type returned by module]: Data returned by module. If any.
    """

    args = list()
    kwargs = dict()

    module_signature = inspect.signature(eval(module_name_string))
    for module_param_name in module_signature.parameters.keys():
        if module_signature.parameters[module_param_name].default is inspect._empty:
            # if default value is not defined, the parameter is positional and mandatory
            if module_param_name in args_dict.keys():
                args.append(args_dict[module_param_name])
            else:
                sys.exit('ERROR: Mandatory positional parameter {} is missing.'.format(module_param_name))
        else:
            if module_param_name in args_dict.keys():
                kwargs.update({
                    module_param_name: args_dict[module_param_name]
                })

    if module_name_string.startswith('runAM'):  # simple way to keep eval() safe
        return eval(module_name_string)(*args, **kwargs)


def parse(cli_spec):
    """Build CLI arguments from cli_spec
    runAM is using argcomplete. To enable autocompletion, follow the docs here:
    https://kislyuk.github.io/argcomplete/
    TL;DR switch to bash and run: eval "$(register-python-argcomplete runAM)"

    Args:
        cli_spec (dict): CLI specification dictionary

    Returns:
        dict: dictionary of CLI arguments
    """

    parser = argparse.ArgumentParser(
        description=cli_spec['__main_parser']['help'], formatter_class=argparse.RawTextHelpFormatter)
    if 'add_argument' in cli_spec['__main_parser'].keys():
        add_arguments(parser, cli_spec['__main_parser']['add_argument'])
    subparsers = parser.add_subparsers(help="Select package", dest='subparser_name')

    for p_name, p_spec in sorted(cli_spec.items()):
        if p_name != '__main_parser':
            subparser = subparsers.add_parser(
                p_name, help=p_spec['help'],
                description=p_spec['help'],
                formatter_class=argparse.RawTextHelpFormatter
            )
            if 'add_argument' in p_spec.keys():
                add_arguments(subparser, p_spec['add_argument'])

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    return vars(args)  # return args dictionary
