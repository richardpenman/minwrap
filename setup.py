import os
from distutils.core import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='ajaxbrowser', 
    version='0.1',
    packages=['ajaxbrowser'],
    package_dir={'ajaxbrowser':'.'}, # look for package contents in current directory
    author='Richard Penman',
    author_email='richard@webscraping.com',
    description='Pure python library aimed to make web scraping easier',
    long_description=read('README.rst'),
    url='http://bitbucket.org/richardpenman/ajaxbrowser',
    license='lgpl',
    install_requires=['demjson', 'lxml'],
)
