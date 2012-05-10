

def to_dot(graph):
    """returns a graph as a graphviz dot string"""
    r = ""

    r += "digraph g {\n"

    for e in graph.get_edges():
        r += '    "%s" -> "%s" [label = "%s"];\n' % \
            (e.start_vertex().get_dbId(), \
             e.end_vertex().get_dbId(), \
             e.get_label())

    r += "}\n"

    return r
