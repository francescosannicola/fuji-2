# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2020 PANGAEA (https://www.pangaea.de/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from fuji_server.evaluators.fair_evaluator import FAIREvaluator
from fuji_server.helper.metadata_collector import MetaDataCollector
from fuji_server.helper.metadata_provider_sparql import SPARQLMetadataProvider
from fuji_server.models.formal_metadata import FormalMetadata
from fuji_server.models.formal_metadata_output_inner import FormalMetadataOutputInner


class FAIREvaluatorFormalMetadata(FAIREvaluator):
    print ("7")

    """
    A class to evaluate that the metadata is represented using a formal knowledge representation language (I1-01M).
    A child class of FAIREvaluator.
    ...

    Methods
    ------
    evaluate()
        This method will evaluate whether the metadata is parsable and has a structured data embedded in the landing page or
        formal metadata, e.g., RDF, JSON-LD, is accessible.
    """

    def evaluate(self):
        self.result = FormalMetadata(id=self.metric_number,
                                     metric_identifier=self.metric_identifier,
                                     metric_name=self.metric_name)

        outputs = []
        score = 0
        test_status = 'fail'

        # note: 'source' allowed values = ["typed_link", "content_negotiate", "structured_data", "sparql_endpoint"]

        # 1. light-weight check (structured_data), expected keys from extruct ['json-ld','rdfa']
        embedded_RDF_exists = False
        self.logger.info('{0} : Check of structured data (RDF serialization) embedded in the data page'.format(
            self.metric_identifier))
        if MetaDataCollector.Sources.SCHEMAORG_EMBEDDED.value in dict(self.fuji.metadata_sources):
            outputs.append(
                FormalMetadataOutputInner(serialization_format='JSON-LD',
                                          source='structured_data',
                                          is_metadata_found=True))
            self.logger.info('{0} : JSON-LD (schema.org) serialization found in the data page - {1}'.format(
                self.metric_identifier, 'JSON-LD'))
            embedded_RDF_exists = True
        if MetaDataCollector.Sources.RDFA_EMBEDDED.value in dict(self.fuji.metadata_sources):
            outputs.append(
                FormalMetadataOutputInner(serialization_format='RDFa', source='structured_data',
                                          is_metadata_found=True))
            self.logger.info('{0} : RDFa serialization found in the data page - {1}'.format(
                self.metric_identifier, 'RDFa'))
            embedded_RDF_exists = True

        if len(outputs) == 0:
            self.logger.info('{0} : NO structured data (RDF serialization) embedded in the data page'.format(
                self.metric_identifier))
        else:
            self.logger.log(
                self.fuji.LOG_SUCCESS,
                '{0} : Found structured data (RDF serialization) in the data page'.format(self.metric_identifier))
            score += 1
            self.maturity = 2
            self.setEvaluationCriteriumScore('FsF-I1-01M-1', 1, 'pass')

        # 2. hard check (typed-link, content negotiate, sparql endpoint)
        # 2a. in the object page, you may find a <link rel="alternate" type="application/rdf+xml" … />

        RDF_link_exists = False
        formalExists = False
        self.logger.info('{0} : Check if RDF-based typed link included'.format(self.metric_identifier))
        if MetaDataCollector.Sources.RDF_TYPED_LINKS.value in dict(self.fuji.metadata_sources):
            self.logger.info('{0} : RDF graph retrieved via typed link, content type - {1}'.format(
                self.metric_identifier, 'RDF'))
            outputs.append(
                FormalMetadataOutputInner(serialization_format='RDF', source='typed_link', is_metadata_found=True))
            #score += 1
            RDF_link_exists = True
            formalExists = True
        else:
            self.logger.info('{0} : NO RDF-based typed link found'.format(self.metric_identifier))

        # 2b.content negotiate
        negotiated_RDF_exists = False
        self.logger.info('{0} : Check if RDF metadata available through content negotiation'.format(
            self.metric_identifier))
        #for rdf_data_sources in [MetaDataCollector.Sources.LINKED_DATA.value, MetaDataCollector.Sources.SCHEMAORG_NEGOTIATE,MetaDataCollector.Sources.]

        if MetaDataCollector.Sources.SCHEMAORG_NEGOTIATED.value in dict(self.fuji.metadata_sources):
            self.logger.info('{0} : JSON-LD graph retrieved through content negotiation, content type - {1}'.format(
                self.metric_identifier, 'JSON-LD'))
            outputs.append(
                FormalMetadataOutputInner(serialization_format='JSON-LD',
                                          source='content_negotiate',
                                          is_metadata_found=True))
            negotiated_RDF_exists = True
            formalExists = True

        if MetaDataCollector.Sources.RDF_NEGOTIATED.value in dict(self.fuji.metadata_sources):
            self.logger.info('{0} : RDF graph retrieved through content negotiation, content type - {1}'.format(
                self.metric_identifier, 'RDF'))
            outputs.append(
                FormalMetadataOutputInner(serialization_format='RDF',
                                          source='content_negotiate',
                                          is_metadata_found=True))
            negotiated_RDF_exists = True
            formalExists = True

        if negotiated_RDF_exists or RDF_link_exists:
            self.logger.log(
                self.fuji.LOG_SUCCESS,
                '{0} : Found RDF content through content negotiation or typed links'.format(self.metric_identifier))
            score += 1
            self.maturity = 3
            self.setEvaluationCriteriumScore('FsF-I1-01M-2', 1, 'pass')
        else:
            self.logger.info('{0} : NO RDF metadata available through content negotiation'.format(
                self.metric_identifier))

        # 2c. try to retrieve via sparql endpoint (if available)
        if not formalExists or 1 == 1:
            # self.logger.info('{0} : Check if SPARQL endpoint is available'.format(formal_meta_identifier))
            # self.sparql_endpoint = 'http://data.archaeologydataservice.ac.uk/sparql/repositories/archives' #test endpoint
            # self.sparql_endpoint = 'http://data.archaeologydataservice.ac.uk/query/' #test web sparql form
            # self.pid_url = 'http://data.archaeologydataservice.ac.uk/10.5284/1000011' #test uri
            # self.sparql_endpoint = 'https://meta.icos-cp.eu/sparqlclient/' #test endpoint
            # self.pid_url = 'https://meta.icos-cp.eu/objects/9ri1elaogsTv9LQFLNTfDNXm' #test uri
            if self.fuji.sparql_endpoint:
                self.logger.info('{0} : SPARQL endpoint found -: {1}'.format(self.metric_identifier,
                                                                             self.fuji.sparql_endpoint))
                sparql_provider = SPARQLMetadataProvider(endpoint=self.fuji.sparql_endpoint,
                                                         logger=self.logger,
                                                         metric_id=self.metric_identifier)
                if self.fuji.pid_url == None:
                    url_to_sparql = self.fuji.landing_url
                else:
                    url_to_sparql = self.fuji.pid_url
                query = 'DESCRIBE <' + str(url_to_sparql) + '>'
                #query = "CONSTRUCT {{?dataURI ?property ?value}} where {{ VALUES ?dataURI {{ <"+str(url_to_sparql)+"> }} ?dataURI ?property ?value }}"
                self.logger.info('{0} : Executing SPARQL -: {1}'.format(self.metric_identifier, query))
                rdfgraph, contenttype = sparql_provider.getMetadata(query)
                if rdfgraph:
                    outputs.append(
                        FormalMetadataOutputInner(serialization_format=contenttype,
                                                  source='sparql_endpoint',
                                                  is_metadata_found=True))
                    if score < 2:
                        score += 1
                    self.maturity = 3
                    self.logger.log(self.fuji.LOG_SUCCESS,
                                    '{0} : Found RDF content through SPARQL endpoint'.format(self.metric_identifier))
                    self.setEvaluationCriteriumScore('FsF-I1-01M-2', 1, 'pass')
                    self.fuji.namespace_uri.extend(sparql_provider.getNamespaces())
                else:
                    self.logger.warning('{0} : NO RDF metadata retrieved through the sparql endpoint'.format(
                        self.metric_identifier))
            else:
                self.logger.warning(
                    '{0} : NO SPARQL endpoint found through re3data based on the object URI provided'.format(
                        self.metric_identifier))

        if score > 0:
            test_status = 'pass'
        self.result.test_status = test_status
        self.score.earned = score
        self.result.metric_tests = self.metric_tests
        self.result.score = self.score
        self.result.maturity = self.maturity
        self.result.output = outputs
