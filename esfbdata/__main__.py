#!/usr/bin/env python
import sys


if __package__ is None and not hasattr(sys, 'frozen'):
    # Fix path for direct call of __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))


import logging
from .options import ArgumentParser
from .events import FacebookEventsIngester
from .messenger import FacebookMessengerIngester
from .timeline import FacebookTimelineIngester


def _main(argv=None):
    'This is the actual main'
    # Get the logger
    logger = logging.getLogger('esfbdata')
    # Parse the arguments
    parser = ArgumentParser()
    args = parser.parse_args(argv)
    # If verbose set logger to info
    if args.verbose:
        logger.setLevel(logging.INFO)
    # If debug set logger to debug
    if args.debug:
        logger.setLevel(logging.DEBUG)
    # Create the console log handler
    ch = logging.StreamHandler()
    # Create the logging formatter
    formatter = logging.Formatter(args.log_format)
    # Add the formatter to the console handler
    ch.setFormatter(formatter)
    # Add the hander to the logger
    logger.addHandler(ch)
    # Build the kwargs from arguments to just pass to the ingesters
    logger.debug('Generating kwargs from user arguments')
    excluded_args = [
        'version',
        'log_format',
        'debug',
        'verbose',
        'ingest',
        'archives']
    kwargs = {
        k: v for k, v in vars(args).iteritems() if k not in excluded_args}
    for archive in args.archives:
        if 'events' in args.ingest:
            logger.debug('Opening events archive')
            events_archive = archive.open('html/events.htm')
            logger.debug('Creating instance of events ingester')
            ingester = FacebookEventsIngester(events_archive, **kwargs)
            logger.info('Ingesting events data')
            ingester.ingest()
        if 'messenger' in args.ingest:
            logger.debug('Opening messenger archive')
            messenger_archive = archive.open('html/messages.htm')
            logger.debug('Creating instance of messenger ingester')
            ingester = FacebookMessengerIngester(messenger_archive, **kwargs)
            logger.info('Ingesting messenger data')
            ingester.ingest()
        if 'timeline' in args.ingest:
            logger.debug('Opening timeline archive')
            timeline_archive = archive.open('html/timeline.htm')
            logger.debug('Creating instance of timeline ingester')
            ingester = FacebookTimelineIngester(timeline_archive, **kwargs)
            logger.info('Ingesting timeline data')
            ingester.ingest()


def main(argv=None):
    'This is a wrapper for main that handles usual suspects'
    try:
        _main(argv)
    except KeyboardInterrupt:
        sys.exit('\nInterrupted by user')


if __name__ == '__main__':
    main()


__all__ = ['main']
