#!/usr/bin/env python
from .ingester import FacebookIngester
import dateutil.parser as dateparser


class FacebookTimelineIngester(FacebookIngester):
    """Elasticsearch ingester for Facebook Timeline HTML archives."""
    def __init__(self, *args, **kwargs):
        if 'document_type' not in kwargs:
            kwargs['document_type'] = 'timeline'
        super(FacebookTimelineIngester, self).__init__(*args, **kwargs)

    def documents(self):
        'Generates Facebook Timeline documents from a souped Facebook export'
        # Get the name of the user who is the account owner who exported
        # the data and is the recipient or publisher of all of this data.
        user = unicode(self.soup.h1.string)
        self.logger.debug('Parsed user - %s', user)
        # Iterate based on the timestamp meta
        for meta in self.soup('div', class_='meta'):
            # Working document
            document = {'user': user}
            # Parse the timestamp of the message
            timestamp = unicode(meta.string)
            timestamp = dateparser.parse(timestamp)
            self.logger.debug('Parsed document timestamp - %s', timestamp)
            # Put it in the document
            document['timestamp'] = timestamp
            # Create a ref for iterating over until the <p></p> delimiter
            current_sibling = meta.next_sibling
            while current_sibling is not None and current_sibling.name != 'p':
                if current_sibling.name is None:
                    # Current sibling is the post body
                    # this is not what the user wrote, actually
                    # That is put in a div with a class of comment
                    document['text'] = unicode(current_sibling.string)
                    self.logger.debug(
                        'Parsed document text - %s',
                        document['text'])
                elif current_sibling.name == 'div':
                    self.logger.debug('Found div element')
                    # Check for div types
                    if 'class' in current_sibling.attrs:
                        class_ = current_sibling.attrs['class']
                        if 'comment' in class_:
                            # This is the poster comment
                            document['comment'] = unicode(
                                current_sibling.string)
                            self.logger.debug(
                                'Parsed document comment - %s',
                                document['comment'])
                        else:
                            # I don't know this class so warn user
                            self.logger.warning(
                                'Unknown div class "%s"',
                                class_)
                    else:
                        # I don't know what this is so warn user if we see it
                        self.logger.warning('Skipping unknown classless div')
                else:
                    # I don't know what this is so warn user
                    self.logger.warning(
                        'Skipping unknown tag "%s"',
                        current_sibling.name)
                # Iterate to the next sibling
                current_sibling = current_sibling.next_sibling
            # Yield the finished dict
            self.logger.debug('Yielding document - ', document)
            yield document

    @classmethod
    def document_id(cls, message):
        'Get the id of a message'
        self.logger.debug('Generating document ID')
        return u'{}:{}'.format(
            message['timestamp'],
            message['user'].replace(' ', ''))


__all__ = ['FacebookTimelineIngester']
