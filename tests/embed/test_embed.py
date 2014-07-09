import subprocess

class Test:

    def test_etc_hosts(self):
        """Check that /etc/hosts has been prepared (see development.rst)."""

        # FIXME: if this test fails, do not crash, but warn and mark all
        # tests in this class as "pending" before continuing.

        assert subprocess.call(["grep", "-q", "adhocracy.embeddee.goo", "/etc/hosts"]) == 0
        assert subprocess.call(["grep", "-q", "adhocracy.embedder.gaa", "/etc/hosts"]) == 0

    def test_acceptance_zooming(self, browser_embedder_root):
        """Run acceptance test after zooming in on iframe."""

        # This is mostly interesting as an example on how to do acceptance
        # tests in general; we may want to re-factor /tests/acceptance so that
        # all the code there can be run both in the non-embed case and in any
        # one of many embedding contexts.

        with browser_embedder_root.get_iframe('adhocracy-iframe') as iframe:
            element = iframe.find_by_css('.login [name="name"]').first
            assert element != None

    def test_resize_message(self, browser_embedder_root):
        """Resize messages from iframe to embedder window."""
        print("\n\n\npending!\n\n\n")
        assert True
