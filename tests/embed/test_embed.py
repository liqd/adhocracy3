
class Test:

    # if /etc/hosts has not been prepared (see development.rst), mark
    # all tests in this class as "pending" before continuing.
    @disable
    def test_etc_hosts(self, browser_sample_root):
        assert True

    # test acceptance test after zooming in on iframe.
    @pending
    def test_acceptance_zooming(self, browser_sample_root):
        assert True

    # test test resize messages from iframe to embedder window.
    def test_resize_message(self, browser_sample_root):
        assert True


# FIXME: disable and pending may not *really* be valid decorators.
# which is the right one?
