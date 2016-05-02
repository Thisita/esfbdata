#!/usr/bin/env python
from .ingester import FacebookIngester
import dateutil.parser as dateparser
import re


class FacebookEventsIngester(FacebookIngester):
    """Elasticsearch ingester for Facebook Events HTML archives."""
    def __init__(self, *args, **kwargs):
        if 'document_type' not in kwargs:
            kwargs['document_type'] = 'event'
            kwargs['timestamp_key'] = 'begin'
        super(FacebookEventsIngester, self).__init__(*args, **kwargs)
        # Compile the re for matching the meta field
        self.logger.debug('Compiling event metadata regular expression parser')
        self.meta_re = re.compile(r'^((?P<location>.+) )?'
            r'(?P<begin>[A-Z][a-z]{5,8}, [A-Z][a-z]{2,8} \d{1,2}, \d{4} at '
            r'\d{1,2}:\d{2}(am|pm) ([A-Z]{1,5}|UTC[+-]\d{1,2}))( - '
            r'(?P<end>[A-Z][a-z]{5,8}, [A-Z][a-z]{2,8} \d{1,2}, \d{4} at '
            r'\d{1,2}:\d{2}(am|pm) ([A-Z]{1,5}|UTC[+-]\d{1,2})))$')

    def documents(self):
        'Generates Facebook Event documents from a souped Facebook export'
        # Get the name of the user who is the account owner who exported
        # the data and is the recipient or publisher of all of this data.
        user = unicode(self.soup.h1.string)
        self.logger.debug('Parsed user - %s', user)
        # Cache the meta_re
        meta_re = self.meta_re
        # Iterate over each of the Events
        # This is actually the most sensical of the archive formats
        for event in self.soup.div.next_sibling.ul('li'):
            # Create a document to work on
            document = {'user': user}
            # Grab the strings
            strings = list(event.strings)
            # The text is the first owner
            text = unicode(strings[0])
            document['text'] = text
            self.logger.debug('Parsed document text - %s', text)
            # The next string is the metadata
            # It is complicated so I just re it
            meta = meta_re.match(unicode(strings[1])).groupdict()
            if 'location' in meta:
                document['location'] = meta['location']
                self.logger.debug(
                    'Parsed document location - %s',
                    meta['location'])
            else:
                self.logger.debug('No location parsed')
            if 'begin' in meta:
                document['begin'] = dateparser.parse(meta['begin'])
                self.logger.debug(
                    'Parsed document begin time - %s',
                    meta['begin'])
            else:
                self.logger.warning(
                    'No begin parsed: This will result in @timestamp being '
                    'null')
            if 'end' in meta:
                document['end'] = dateparser.parse(meta['end'])
                self.logger.debug(
                    'Parsed document end time - %s',
                    meta['end'])
            else:
                self.logger.debug('No end time parsed')
            # If there is a third string, it the user's attendance
            if len(strings) == 3:
                attendance = unicode(strings[2])
                document['attendance'] = attendance
                self.logger.debug('Parsed attendance - %s', attendance)
            else:
                self.logger.debug('No attendance statement parsed')
            # Yield out the document
            self.logger.debug('Yielding document - ', document)
            yield document

    @classmethod
    def document_id(cls, message):
        'Get the id of a message'
        if 'end' in message:
            self.logger.debug('Generating document ID with end date')
            return u'{}:{}:{}'.format(
                message['begin'],
                message['end'],
                message['user'].replace(' ', ''))
        else:
            self.logger.debug('Generating document ID without end date')
            return u'{}:{}'.format(
                message['begin'],
                message['user'].replace(' ', ''))


__all__ = ['FacebookEventsIngester']
