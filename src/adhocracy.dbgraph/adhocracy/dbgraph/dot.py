

from tempfile import NamedTemporaryFile
from subprocess import check_call
from subprocess import check_output


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


def to_pdf(filename, graph):
    with NamedTemporaryFile(mode="w") as dotFile:
        dotFile.write(to_dot(graph))
        dotFile.flush()
        print(check_output(["dot", dotFile.name, "-Tpdf", "-o", filename]))
