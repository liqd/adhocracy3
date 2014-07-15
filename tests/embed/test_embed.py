import subprocess
from time import sleep

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
            elements = iframe.find_by_css('#document_workbench_list')
            assert len(elements) != 0 and elements.first != None

    def test_resize(self, browser_embedder_root):
        """Iframe height matches its content after at most 5 seconds."""

        sec = 0
        js = 'document.getElementById("adhocracy-iframe").clientHeight'

        while True:
            outer_height = browser_embedder_root.evaluate_script(js)

            with browser_embedder_root.get_iframe('adhocracy-iframe') as iframe:
                inner_height = iframe.evaluate_script('document.body.clientHeight')

                if outer_height == inner_height:
                    break
                elif sec <= 5:
                    sec += 1
                    sleep(1)
                else:
                    assert outer_height == inner_height
