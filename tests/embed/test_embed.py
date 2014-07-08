
class Test:

    # if /etc/hosts has not been prepared (see development.rst), mark
    # all tests in this class as "pending" before continuing.
    def test_etc_hosts(self, browser_embedder_root):
        assert True

    # test acceptance test after zooming in on iframe.
    def test_acceptance_zooming(self, browser_embedder_root):
        assert True

    # resize messages from iframe to embedder window.
    def test_resize_message(self, browser_embedder_root):
        assert True
