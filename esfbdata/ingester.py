#!/usr/bin/env python
import logging
from elasticsearch import Elasticsearch, TransportError
from elasticsearch.helpers import bulk
from bs4 import BeautifulSoup


class FacebookIngester(object):
    'Elasticsearch ingester for Facebook HTML archives.'
    def __init__(self, archive, nodes, index, document_type,
            timestamp_key='timestamp', parser='html.parser', ignore=400,
            retry_on_timeout=True, max_retries=10, simulate=False):
        super(FacebookIngester, self).__init__()
        # Set up logging
        self.logger = logging.getLogger('esfbdata')
        # The parser to be used by BeautifulSoup
        self.logger.debug('BeautifulSoup parser set to %s', parser)
        self.parser = parser
        # The Elasticsearch index to ingest data into
        self.logger.debug('Elasticsearch index set to %s', index)
        self.index = index
        # The document type to mark each Elasticsearch document as on ingest
        self.logger.debug(
            'Elasticsearch document type set to %s', document_type)
        self.document_type = document_type
        # The document key to use for @timestamp
        self.logger.debug('@timestamp mapping set to %s', timestamp_key)
        self.timestamp_key = timestamp_key
        # Whether or not to actually index data in Elasticsearch
        self.logger.debug('Simulation set to %s', simulate)
        if simulate:
            self.logger.info(
                'Running in simulation mode - No documents will be sent to '
                'Elasticsearch')
        self.simulate = simulate
        # The soup to easily parse through the Facebook HTML archive with
        self.logger.debug('Creating BeautifulSoup instance')
        self.logger.info('Parsing HTML')
        self.soup = BeautifulSoup(archive, self.parser)
        # The Elasticsearch cluster to ingest data into
        self.logger.debug(
            'Ignoring Elasticsearch responses with code(s) %s', ignore)
        self.logger.debug(
            'Elasticsearch retry on different node set to %s',
            retry_on_timeout)
        self.logger.debug('Elasticsearch max retries set to %d', max_retries)
        self.logger.debug('Creating Elasticsearch instance')
        self.es = Elasticsearch(
            nodes,
            ignore=ignore,
            retry_on_timeout=retry_on_timeout,
            max_retries=max_retries)

    def documents(self):
        'Generates Facebook documents from a souped Facebook export'
        # Not Implemented as this is abstract
        raise NotImplementedError()

    @classmethod
    def document_id(cls, document):
        'Get the id of a document'
        self.logger.debug('Generating document ID - Default handler')
        # default use the @timestamp as the doc_id
        return str(document[self.timestamp_key])

    def actions(self):
        'Generates Elasticsearch bulk actions'
        # Iterate over all of the messages
        self.logger.debug('Generating documents')
        for document in self.documents():
            # Add @timestamp
            self.logger.debug('Inserting @timestamp')
            document['@timestamp'] = document[self.timestamp_key]
            # Generate index actions
            if not self.simulate:
                self.logger.debug(
                    'Sending document to Elasticsearch bulk queue')
                yield {
                    '_index': self.index,
                    '_type': self.document_type,
                    '_id': self.document_id(document),
                    '_source': document}

    def ingest(self):
        'Ingest documents into Elasticsearch'
        # Use the bulk API to queue up the requests and generally
        # reduce the stress on ingest
        self.logger.debug('Calling Elasticsearch bulk helper')
        success, _ = bulk(self.es, self.actions(), raise_on_exception=False)
        self.logger.info('Elasticsearch success = %d', success)
        self.logger.debug('Elasticsearch bulk data - %s', _)


__all__ = ['FacebookIngester']
