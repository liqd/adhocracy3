import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'rwproperty',
    'bulbs==0.3-20120331',
    'zope.component>=3.11.0', #make config.hook_zca() work
    'pyramid',
    'pyramid_tm',
    'pyramid_zcml',
    'pyramid_debugtoolbar',
    'waitress',
    ]

setup(name='adhocracy.core',
      version='0.0',
      description='adhocracy.core',
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
      keywords='web pylons pyramid',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      tests_require= requires,
      test_suite="adhocracy.core",
      namespace_packages=['adhocracy'],
      entry_points = """\
      [paste.app_factory]
      main = adhocracy.core:main
      """,
      )

