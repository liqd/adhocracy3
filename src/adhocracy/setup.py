import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, '../../README.rst')).read()
CHANGES = open(os.path.join(here, '../../CHANGES.rst')).read()

requires = [
    'pyramid_chameleon',
    'pyramid',
    'pyramid_debugtoolbar',
    'waitress',
    'substanced',
    'pyramid_tm',
    'cornice',
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
      tests_require=requires,
      test_suite="adhocracy",
      entry_points="""\
      [paste.app_factory]
      main = adhocracy:main
      """,
      )

