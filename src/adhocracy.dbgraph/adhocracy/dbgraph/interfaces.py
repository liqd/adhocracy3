from zope.interface import Interface


class IElement(Interface):
    """
    Graph element object.
    """

    def get_property(key):
        """Gets the value of the property for the given key"""

    def get_properties():
        """Returns a dictionary with all properties (key/value)"""

    def set_property(key, value):
        """Sets the property of the element to the given value"""

    def set_properties(property_dictionary):
        """Add properties. Existing properties are replaced."""

    def remove_property(self, key):
        """Removes the value of the property for the given key"""

    def get_dbId(self):
        """Returns the unique identifier of the element"""

    def get_main_interface():
        """Returns the main interface property (string)"""

    def initialize():
        """Apply main interface.
           The main interface is stored in the
           main_interface" property,
        """


class IVertex(IElement):
    """
    Graph vertex object.
    """


class IEdge(IElement):
    """
    Graph edge object.
    """

    def get_property(key):
        """Gets the value of the property for the given key"""

    def get_properties():
        """Returns a dictionary with all properties (key/value)"""

    def set_property(key, value):
        """Sets the property of the element to the given value"""

    def set_properties(property_dictionary):
        """Add properties. Existing properties are replaced."""

    def remove_property(self, key):
        """Removes the value of the property for the given key"""

    def get_dbid(self):
        """Returns the database id of the element"""

    def get_main_interface():
        """Returns the main interface."""

    def initialize():
        """Apply main interface that is stored in the
           main_interface" property,
        """


class IGraphConnection(Interface):
    """
    The graph connection object.
    """

    def add_vertex(main_interface=IVertex):
        """Adds a new vertex to the graph with the given
           Interface.
        """

    def get_vertex(dbid):
        """Retrieves an existing vertex from the graph
           with the given dbid or None.
        """

    def get_vertices():
        """Returns an iterator with all the vertices"""

    def remove_vertex(vertex):
        """Removes the given vertex"""

    def add_edge(self, startVertex, endVertex, label, main_interface=IEdge):
        """Creates a new edge with label(String)"""

    def get_edge(dbid):
        """Retrieves an existing edge from the graph
           with the given dbid or None.
        """

    def get_edges():
        """Returns an iterator with all the vertices"""

    def remove_edge(edge):
        """Removes the given edge"""

    def clear():
        """Dooms day machine"""

    def start_transaction():
        """Start Transaction to add new or create Elements"""

    def stop_transaction():
        """Stop Transaction"""
