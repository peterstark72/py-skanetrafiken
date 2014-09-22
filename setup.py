#!/usr/bin/env python

from distutils.core import setup

setup(name='skanetrafiken',
      version='2.0.1',
      py_modules=['skanetrafiken'],
      author='Peter Stark',
      author_email='peterstark72@gmail.com',
      url='https://github.com/peterstark72/skanetrafiken',
      install_requires=['lxml'],
      description="Python wrapper for Skanetrafiken Open API",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: Free for non-commercial use',
                   'Natural Language :: Swedish',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Internet']
      )
