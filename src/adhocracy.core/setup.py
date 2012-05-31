import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'rwproperty',
    'adhocracy.dbgraph',
    'zope.component>=3.11.0',  # make config.hook_zca() work
    'zope.configuration>=3.8.0dev',
    'zope.dottedname',
    'repoze.lemonade',
    'pyramid',
    'pyramid_zcml>=0.8',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'pyramid_adoptedtraversal',
    'waitress',
    ]

tests_requires = [
    'WebTest',
    'mock',
    'pytest',
    'pytest-cov',
    'pytest-pep8',
    'wsgi_intercept',
    'zope.testbrowser',
    ]

setup(name='adhocracy.core',
      version='0.0',
      description='adhocracy.core',
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
      keywords='web pylons pyramid',
      packages=find_packages(exclude=['ez_setup']),
      #package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=tests_requires,
      namespace_packages=['adhocracy'],
      entry_points="""\
      [paste.app_factory]
      main = adhocracy.core:main
      """,
      extras_require={
          'test': tests_requires,
          },
      )
