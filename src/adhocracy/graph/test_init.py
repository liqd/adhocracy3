from . import is_ancestor


def test_is_ancestor():
    pass

# TODO test cases:
# False if ancestor is None
# False if descendant is None
# True if ancestor == descendant
# True if direct element link from A to D
# True if indirect element/contains/comments link from A to D
# False if direct follows link from A to D
# False if C is element of A and D follows C
# False if direct element link from D to A
