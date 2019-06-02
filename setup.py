#!/usr/bin/env python3
import sys

from setuptools import setup, find_packages

import kubewatch


requires = ['boto3', 'jmespath']


setup_options = dict(
    name='kubewatch',
    version=kubewatch.__version__,
    description='kubewatch clone in Python.',
    long_description=open('README.rst').read(),
    author='Hans-Jörg Wieland',
    url='',
    scripts=['bin/kubewatch'],
    packages=find_packages(exclude=['tests*']),
    package_data={'awskubewatchk8snmap': []},
    install_requires=requires,
    extras_require={
        ':python_version>="3.6"': [
            'argparse>=1.1',
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
        'Programming Language :: Python :: 3.6',
    ),
)

if 'py2exe' in sys.argv:
    # This will actually give us a py2exe command.
    import py2exe
    # And we have some py2exe specific options.
    setup_options['options'] = {
        'py2exe': {
            'optimize': 0,
            'skip_archive': True,
            'dll_excludes': ['crypt32.dll'],
            'packages': ['docutils', 'urllib', 'httplib', 'HTMLParser',
                         'awscli', 'ConfigParser', 'xml.etree', 'pipes'],
        }
    }
    setup_options['console'] = ['bin/aws']


setup(**setup_options)