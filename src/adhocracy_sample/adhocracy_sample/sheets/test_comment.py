import unittest

from pyramid import testing

from adhocracy.utils import get_sheet


class CommentSheetIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy_sample.sheets.comment')

    def tearDown(self):
        testing.tearDown()

    def test_create_comment_sheet(self):
        from adhocracy_sample.sheets.comment import IComment
        context = testing.DummyResource(__provides__=IComment)
        inst = get_sheet(context, IComment)
        assert inst.meta.isheet is IComment
