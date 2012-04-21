import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'adhocracy.core',
    ]

setup(name='Adhocracy',
      version='0.0',
      description='Buildout to install Adhocracy',
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
      #package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = adhocracy.core:main
      """,
      )

