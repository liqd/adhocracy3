import time
import sys
import logging

from repoze.sendmail.queue import (
    ConsoleApp,
    string_or_none,
    boolean,
    )
from pyramid.paster import get_appsettings

class CustomConsoleApp(ConsoleApp):
    def _load_config(self, path=None):
        if path is None:
            # called at construction time as None, later called
            # with real config due to --config argument
            return
        settings = get_appsettings(path)
        prefix = settings.get('pyramid_mailer.prefix', 'mail.')
        mailsettings = {}
        for k, v in settings.items():
            if k.startswith(prefix):
                mailsettings[k[len(prefix):]] = v
        self.queue_path = mailsettings['queue_path']
        self.hostname = mailsettings.get('host', 'localhost')
        self.port = int(mailsettings.get('port', 25))
        self.username = string_or_none(mailsettings.get('username'))
        self.password = string_or_none(mailsettings.get('password'))

        tls = mailsettings.get('tls')
        if tls is None:
            self.no_tls = False
            self.force_tls = False
        elif tls:
            self.no_tls = False
            self.force_tls = True
        else:
            self.no_tls = True
            self.force_tls = False
            
        self.ssl = boolean(mailsettings.get('ssl'))
        self.debug_smtp = string_or_none(mailsettings.get('debug'))

def main(argv=sys.argv):
    logging.basicConfig(
        format='%(asctime)s %(message)s'
        )
    if not '--config' in argv:
        print "You must pass --config some_config_file.ini"
        sys.exit(2)
    app = CustomConsoleApp(argv)
    app.main()
    time.sleep(15) # wait 15 seconds before exiting, to be runnable via supervisor
    
