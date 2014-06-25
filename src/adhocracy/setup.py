import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, '../../README.rst')).read()
CHANGES = open(os.path.join(here, '../../CHANGES.rst')).read()

requires = [
    'pyramid_chameleon',
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_exclog',
    'waitress',
    'substanced',
    'pyramid_tm',
    'cornice',
    'autobahn',
    'asyncio',
    'websocket-client-py3',
    ]

test_requires = [
    'pytest',
    'selenium',
    'webtest',
    'pytest-splinter',
    'pytest-quickcheck',
    'pytest-pyramid',
    'requests',
]


setup(name='adhocracy',
      version='0.0',
      description='adhocracy',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons substanced',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require={'test': test_requires},
      entry_points="""\
      [paste.app_factory]
      main = adhocracy:main
      [pytest11]
      adhocracy = adhocracy.testing
      [console_scripts]
      start_ws_server = adhocracy.websockets.start_ws_server:main
      """,
      )

