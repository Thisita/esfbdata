#!/usr/bin/env python
import argparse
from zipfile import ZipFile
from .version import __version__
from .description import __description__


class ArgumentParser(argparse.ArgumentParser):
    'Option parser for Facebook archive and Elasticsearch options.'
    def __init__(self, **kwargs):
        if 'prog' not in kwargs:
            kwargs['prog'] = 'esfbdata'
        if 'description' not in kwargs:
            kwargs['description'] = __description__
        super(ArgumentParser, self).__init__(**kwargs)
        self.add_argument('--version',
            action='version',
            version='%(prog)s {version}'.format(version=__version__))
        self.add_argument('archives',
            metavar='FILE',
            help='The Facebook archives to ingest',
            nargs='+',
            type=ZipFile)
        self.add_argument('-n', '--nodes',
            metavar='NODE',
            help='Elasticsearch nodes to connect to',
            nargs='+',
            required=True)
        self.add_argument('-i', '--index',
            help='Elasticsearch index to ingest data into '
            '(default: %(default)s)',
            default='facebook')
        self.add_argument('--ignore',
            metavar='STATUS_CODE',
            help='Elasticsearch errors to ignore (default: %(default)s)',
            nargs='+',
            type=int,
            default=[400])
        self.add_argument('--parser',
            help='HTML parser to use (default: %(default)s)',
            choices=['html.parser', 'lxml', 'html5lib'],
            default='html.parser')
        self.add_argument('--ingest',
            help='Set archives to ingest (default: %(default)s)',
            nargs='+',
            choices=['events', 'messenger', 'timeline'],
            default=['events', 'messenger', 'timeline'])
        self.add_argument('-v', '--verbose',
            help='Set log level to INFO',
            action='store_true')
        self.add_argument('-d', '--debug',
            help='Set log level to DEBUG (supercedes --verbose)',
            action='store_true')
        self.add_argument('--log-format',
            help='Set the format of logs (default: %(default)s)',
            default='%(asctime)s - %(levelname)s - %(message)s')
        self.add_argument('-s', '--simulate',
            help='Skip indexing of data',
            action='store_true')


__all__ = ['ArgumentParser']
