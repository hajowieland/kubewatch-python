#!/usr/bin/env python3
import sys

from setuptools import setup, find_packages

import kubewatch


requires = ['requests', 'asyncio']


setup_options = dict(
    name='kubewatch',
    version=kubewatch.__version__,
    description='kubewatch clone in Python.',
    long_description=open('README.md').read(),
    author='Hans-Jörg Wieland',
    url='',
    scripts=['kubewatch.py'],
    packages=find_packages(exclude=['tests*']),
    package_data={'awskubewatchk8snmap': []},
    install_requires=requires,
    extras_require={
        ':python_version>="3.7"': [
            'asyncio>=3.4.3',
            'kubernetes_asyncio>=10.0.0',
            'prometheus_client>=0.7.1',
            'requests>=2.22.0',
        ]
    },
    license="Apache License 2.0",
    classifiers=(
        'Topic :: Security',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ),
)

setup(**setup_options)