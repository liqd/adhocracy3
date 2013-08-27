#
# Evolve scripts for the sdidemo
#

import logging

logger = logging.getLogger('evolution')

def say_hello(root):
    logger.info(
        'Running sdidemo evolve step 1: say hello'
    )

def includeme(config):
    config.add_evolution_step(say_hello)
    
