# -*- coding: utf-8 -*-

from neo4j import GraphDatabase

from zope.interface import implements

from adhocracy.dbgraph.interfaces import IGraphConnection


class EmbeddedGraphConnection():
    implements(IGraphConnection)

    def __init__(self, connection_string):

        self.db = GraphDatabase(connection_string)


    def shutdown(self):

        self.db.shutdown()

    def start_transaction(self):
        pass

