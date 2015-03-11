""""Adhocracy meta package for Mercator."""
import os
import version

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = ['adhocracy_mercator',
            'adhocracy_frontend',
            ]

test_requires = ['adhocracy_mercator[test]',
                 'adhocracy_frontend[test]',
                 ]

debug_requires = ['adhocracy_mercator[debug]',
                  'adhocracy_frontend[debug]',
                  ]


setup(name='mercator',
      version=version.get_git_version(),
      description='Adhocracy backend/frontend server for Mercator.',
      long_description=README + '\n\n' + CHANGES,
      classifiers=["Programming Language :: Python",
                   "Framework :: Pylons",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
                   ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons adhocracy',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      extras_require={'test': test_requires,
                      'debug': debug_requires,
                      },
      entry_points="""\
      [paste.app_factory]
      main = mercator:main
      """,
      )
