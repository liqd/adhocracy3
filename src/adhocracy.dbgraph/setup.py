import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'setuptools',
    'zope.dottedname',
    'pyramid',
    'pyramid_debugtoolbar',
    'waitress',
    'JPype',
    'neo4j-embedded',
    ]

tests_require = [
    'pytest',
    'pytest-cov',
    'pytest-pep8',
    'pytest-quickcheck',
    ]

setup(name='adhocracy.dbgraph',
      version='0.0',
      description='adhocracy.dbgraph',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      namespace_packages=["adhocracy"],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=tests_require,
      entry_points="""\
      [paste.app_factory]
      """,
      extras_require={
          'test': tests_require,
          },
      )
