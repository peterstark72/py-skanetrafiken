from setuptools import setup

setup(name='skanetrafiken',
      version='2.2.0',
      py_modules=['skanetrafiken'],
      author='Peter Stark',
      author_email='peterstark72@gmail.com',
      url='https://github.com/peterstark72/py-skanetrafiken',
      install_requires=['lxml'],
      setup_requires=['wheel'],
      description="Python wrapper for Skanetrafiken Open API",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: Free for non-commercial use',
                   'Natural Language :: Swedish',
                   'Programming Language :: Python :: 3.5',
                   'Topic :: Internet']
      )
