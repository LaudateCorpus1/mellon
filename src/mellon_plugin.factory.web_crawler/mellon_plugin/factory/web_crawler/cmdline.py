"""
Allow use of native Scrapy CLI app with Mellon config based scrapers.
"""
import mellon.mellon
import mellon_plugin.factory.web_crawler
from mellon.mellon import getScriptArgumentParser
import os
import scrapy.cmdline
import sys

def get_cli_args():
    """Return 2 entry tuple

    First entry are Mellon compatible args
    Second are Scrapy compatible args
    """
    _mellon, _scrapy = [], []
    for i, arg in enumerate(sys.argv):
        if not i:
            _mellon.append(arg)
            _scrapy.append(arg)
        if i == 1:
            _mellon.append(arg)
        if i > 1:
            if arg in ['--verbose', '--debug']:
                _mellon.append(arg)
            else:
                _scrapy.append(arg)
    return (_mellon, _scrapy, )


def main():
    cwd = os.getcwd()
    try:
        # get argv's for mellon vs scrapy apps
        args_mellon, args_scrapy = get_cli_args()
        # We'll create and register a Mellon app.  this will allow
        # Scrapy components to find the app config via registry look-ups.
        sys.argv = args_mellon
        args = getScriptArgumentParser(mellon.mellon.DESCRIPTION).parse_args()
        mellon.mellon.create_and_register_app(args.config_file, args.verbose, args.debug)
        # run scrapy (from scrapy project dir)
        sys.argv = args_scrapy
        os.chdir(os.path.dirname(mellon_plugin.factory.web_crawler.__file__))
        sys.path.append(os.path.dirname(__file__))
        scrapy.cmdline.execute()
    finally:
        os.chdir(cwd)

if __name__ == '__main__':
    main()
