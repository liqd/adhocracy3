
class Test:

    # if /etc/hosts has not been prepared (see development.rst), mark
    # all tests in this class as "pending" before continuing.
    def test_etc_hosts(self, browser_embedder_root):
        assert True

    # run acceptance test after zooming in on iframe.  (this is mostly
    # interesting as an example on how to do acceptance tests in
    # general; we may want to re-factor /tests/acceptance so that all
    # the code there can be run both in the non-embed case and in any
    # one of many embedding contexts.)
    def test_acceptance_zooming(self, browser_embedder_root):
        with browser_embedder_root.get_iframe('adhocracy_iframe') as iframe:
            element = iframe.find_by_css('.login [name="name"]').first
            assert element != None

    # resize messages from iframe to embedder window.
    def test_resize_message(self, browser_embedder_root):
        assert True
