#!/usr/bin/env python
from distutils.core import setup


# Get the description without importing
exec(compile(open('esfbdata/description.py').read(),
    'esfbdata/description.py', 'exec'))
# Get the version without importing
exec(compile(open('esfbdata/version.py').read(),
    'esfbdata/version.py', 'exec'))


setup(
    name='esfbdata',
    version=__version__,
    description=__description__,
    license='GNU General Public License (GPL), version 3',
    url='https://gitlab.com/thisita/esfbdata',
    author='Ian Zachary Ledrick',
    author_email='thisita@outlook.com',
    packages=['esfbdata'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later '
        '(GPLv3+)',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'],
    install_requires=[
        'elasticsearch',
        'beautifulsoup4',
        'dateutil'],
    scripts=['bin/esfbdata'])
