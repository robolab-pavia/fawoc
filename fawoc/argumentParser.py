import abc
import argparse


class SlrKitAction(argparse.Action, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def slrkit_conf_default(self):
        raise NotImplementedError


class ArgParse(argparse.ArgumentParser):
    """
    Custom ArgumentParser that allows to collect and retrieve information about
    the configurated arguments.

    This subclass adds an slrkit_arguments attribute: this attribute is a dict
    with the name of the argument as the key, and a dict of information about
    the argument as the value.
    The value contains the following data:
    * value: the default value of the argument;
    * help: the help text of the argument as printed by argparse;
    * required: wheter this argument is required or not;
    * dest: the name of the Namespace field for this argument (see 'dest' in
      the original argparse add_argument documentation);
    * non-standard: signals that this argument requires a non-standard handling;
    * log: signals that this option is place where the logfile is saved;
    * suggest-suffix: this field suggest a custom suffix to be suggested to
      the user for the value of this option;
    * cli_only: specifies that this argument is intended to be use on the
      command line only.
    """

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.slrkit_arguments = dict()
        return obj

    def add_argument(self, *name_or_flags, **kwargs):
        """
        Define how a single command-line argument should be parsed.

        This is an overridden version of the original add_argument method.
        Refer to the argparse documentation for more information about the
        original behaviour of this method.

        This override collects informations about the argument, and stores them
        in the slrkit_arguments dictionary with the name used as key taken from
        the longest option string specified for this argument (stripped
        by all leading prefix characters), or from the name of the positional
        argument. If the 'action' keyword argument has the 'help' or the
        'version', then no information about this argument is stored as this
        option is internally handled by argparse.
        Some custom keyword arguments are handled by this method. They are:
        * non_standard: bool value, default False, specifies that this argument
          must be handled in special way;
        * logfile: bool value, default False, specifies that this argument is
          the path of a logfile;
        * suggest_suffix: str value, default None, suffix to suggest to the user
          for the value of this argument;
        * cli_only: bool value, default False, specifies that this argument is
          intended to be use on the command line only.
        the value of all of them is stored with the information about the
        argument.
        """
        non_standard = kwargs.pop('non_standard', False)
        log = kwargs.pop('logfile', False)
        suggest = kwargs.pop('suggest_suffix', None)
        cli_only = kwargs.pop('cli_only', None)
        action = kwargs.get('action', 'store')
        ret = super().add_argument(*name_or_flags, **kwargs)
        if action not in ['help', 'version']:
            if ret.option_strings:
                # take the longest option string without leading prefixes as the
                # option name
                options = [o.lstrip(self.prefix_chars) for o in ret.option_strings]
                name = max(options, key=lambda o: len(o))
            else:
                name = ret.dest
            if isinstance(ret, SlrKitAction):
                default = ret.slrkit_conf_default
            else:
                default = ret.default
                if ret.default is None:
                    if action in ['append', 'extend']:
                        default = []
                    elif action == 'store_const':
                        default = False
                    elif action == 'count':
                        default = 0

            self.slrkit_arguments[name] = {
                'value': default,
                'help': ret.help % vars(ret),
                'non-standard': non_standard,
                'required': ret.required,
                'dest': ret.dest,
                'choices': ret.choices,
                'logfile': log,
                'suggest-suffix': suggest,
                'cli_only': cli_only,
            }

        return ret
