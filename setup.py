from setuptools import setup
from pathlib import Path

setup(
    name='macecomp',
    description='Command line application for managing macecomp system',
    version='1.0',
    packages=['macecomp'],
    package_data={
        'macecomp': ['doc/*']
    },
    data_files=[(str(Path.home()), ['macecomp/macecomp_config.json'])],
    entry_points={
        'console_scripts': [
            'macecomp = macecomp.__main__:main'
        ]
    },
    install_requires=[
        'pandas',
        'sqlalchemy',
        'mysql-connector',
        'xlrd',
        'bbrest'
    ]
)
