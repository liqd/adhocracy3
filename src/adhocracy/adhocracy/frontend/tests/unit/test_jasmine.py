from time import sleep

import pytest


class TestJasmine:

    @pytest.fixture()
    def browser_test(self, browser, server_sample):
        url = server_sample.application_url + 'frontend_static/test.html'
        browser.visit(url)
        return browser

    def test_all(self, browser_test):
        while not browser_test.evaluate_script('jsApiReporter.finished'):
            sleep(0.1)
        data = browser_test.evaluate_script('jsApiReporter')

        formatter = Formatter(data)
        print(formatter.format())

        results = data['results_'].values()
        assert(all((r['result'] == 'passed' for r in results)))


class Formatter(object):
    COLORS = {
        'red': '\033[0;31m',
        'green': '\033[0;32m',
        'yellow': '\033[0;33m',
        'none': '\033[0m',
    }

    def __init__(self, data, colors=True):
        """Create Formatter.

        :param data: Data from jasmine's JsApiReporter
        :param colors: enable colors

        """
        self.colors = colors
        self.suites = data['suites_']
        self.results = data['results_']

    def format(self):
        """Format a jasmine data into a string."""
        return '\n\n'.join((self.format_suite(s) for s in self.suites))

    def format_suite(self, suite):
        """Format a jasmine suite into a string."""
        if suite['type'] == 'spec':
            result = self.results[str(suite['id'])]
            result_s = self.format_result(result)
        else:
            result_s = ''
        children = suite['children']
        children_s = '\n\n'.join((self.format_suite(c) for c in children))
        if result_s and children_s:
            s = '{0}\n{1}\n\n{2}'
        elif result_s:
            s = '{0}\n{1}'
        elif children_s:
            s = '{0}\n{2}'
        else:
            s = '{0}'
        return s.format(
            suite['name'],
            self.indent(result_s),
            self.indent(children_s))

    def format_result(self, result):
        """Format a jasmine result into a string."""
        messages = result['messages']
        return '\n'.join((self.format_message(m) for m in messages))

    def format_message(self, message):
        """Format a jasmine message into a string."""
        s = '{1} \'{2}\' {3} \'{4}\' ({0})'.format(
            message['message'],
            message['type'],
            message['actual'],
            message['matcherName'],
            message['expected'])
        s = self.colorize('green' if message['passed_'] else 'red', s)
        return s

    def colorize(self, color, text):
        """Add color markers for console output if colors are enabled."""
        if not self.colors:
            return text

        return self.COLORS[color] + text + self.COLORS['none']

    def indent(self, s, spaces=2):
        """Add `spaces` spaces to the beginning of each line."""
        lines = s.split('\n')
        indented_lines = [' ' * spaces + l for l in lines]
        return '\n'.join(indented_lines)
