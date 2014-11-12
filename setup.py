#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

entrypoints = {}

console_scripts = entrypoints['console_scripts'] = [
    'imi = imi.__main__:main',
]

setup(
    name='imi',
    version='0.1.0',
    description='TODO',
    long_description=readme + '\n\n' + history,
    author='EAMY',
    author_email='team@eamy.org',
    url='https://github.com/eamy-org/imi',
    packages=['imi', 'imi.bin'],
    package_dir={'imi': 'imi'},
    include_package_data=False,
    install_requires=requirements,
    license="MPL-2.0",
    zip_safe=False,
    keywords='imi',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    entry_points=entrypoints,
    test_suite='tests',
    tests_require=test_requirements
)
