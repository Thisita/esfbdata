#!/usr/bin/env python
from .ingester import FacebookIngester
import dateutil.parser as dateparser


class FacebookMessengerIngester(FacebookIngester):
    """Elasticsearch ingester for Facebook Messenger HTML archives."""
    def __init__(self, *args, **kwargs):
        if 'document_type' not in kwargs:
            kwargs['document_type'] = 'message'
        super(FacebookMessengerIngester, self).__init__(*args, **kwargs)

    def documents(self):
        'Generates Facebook Messenger documents from a souped Facebook export'
        # Get the name of the user who is the account owner who exported
        # the data and is the recipient or publisher of all of this data.
        user = unicode(self.soup.h1.string)
        self.logger.debug('Parsed user - %s', user)
        # Iterate over each of the threads the user participated in
        for thread in self.soup('div', class_='thread'):
            # Get the list of thread participants
            participants = unicode(thread.contents[0])
            # Parse the list into an array of individual participant names
            participants = list([p.strip() for p in participants.split(',')])
            self.logger.debug('Parsed thread participants - %s', participants)
            # Iterate over each of the messages in the thread
            for message in thread('div', class_='message'):
                # Facebook stores the author and timestamp data in a header
                # metadata div. I'm not sure why considering that there is
                # nothing else in the message metadata div.
                header = message.find('div', class_='message_header')
                # Parse the author of the message
                author = unicode(header.find('span', class_='user').string)
                self.logger.debug('Parsed document author - %s', author)
                # Parse the timestamp of the message
                timestamp = unicode(header.find('span', class_='meta').string)
                timestamp = dateparser.parse(timestamp)
                self.logger.debug('Parsed document timestamp - %s', timestamp)
                # Parse the body of the message which is a paragraph element
                # sibling to the message metadata div
                text = unicode(message.next_sibling.string)
                self.logger.debug('Parsed document text - %s', text)
                # Yield as a nicely formated dict
                self.logger.debug('Yielding document - ', document)
                yield {
                    'user': user,
                    'participants': participants,
                    'author': author,
                    'timestamp': timestamp,
                    'text': text}

    @classmethod
    def document_id(cls, message):
        'Get the id of a message'
        self.logger.debug('Generating document ID')
        return u'{}:{}:{}'.format(
            message['timestamp'],
            message['user'].replace(' ', ''),
            message['author'].replace(' ', ''))


__all__ = ['FacebookMessengerIngester']
