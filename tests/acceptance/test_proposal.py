from time import sleep


class Test_Proposal:

    """User wants to create and see Proposals with multiple paragraphs."""

    def wait(self, condition, step=0.1, max_steps=10):
        """Wait for a condition to become true."""
        for i in range(max_steps):
            if condition():
                return True
            sleep(step)
        return False

    def create(self, listing, title, description="", paragraphs=[]):
        """Create a new Proposal."""
        listing.find_by_css(".navbar .button").first.click()
        form = listing.find_by_css(".listing-create-form").first

        form.find_by_css("[name='title']").first.fill(title)
        form.find_by_css("[name='description']").first.fill(description)
        for paragraph in paragraphs:
            form.find_by_css("[name='add-paragraph']").first.click()
            form.find_by_css("textarea")[-1].fill(paragraph)

        form.find_by_css("input[type='submit']").first.click()

    def test_create(self, browser, server_sample):
        register_url = server_sample.application_url + 'frontend_static/root.html'
        browser.visit(register_url)
        listing = browser.browser.find_by_css('.moving-column-content .listing').first
        self.create(listing, "sometitle")
        assert browser.browser.is_element_present_by_css(
                '.moving-column-content .listing .listing-element')

        element = listing.find_by_css('.listing-element')
        element_a =element.find_by_css('a').first
        assert self.wait(lambda: element_a.value)
        assert element_a.value == "sometitle"

        element_a.click()
        assert element.find_by_css('h1').first.value == "sometitle"
