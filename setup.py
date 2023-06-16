from setuptools import setup

from vCenterScripter.common import __version__

setup(
    name='vCenterScripter',
    version=__version__,
    url='https://github.com/P923/',
    py_modules=['vCenterScripter'],
    install_requires=[
        'pyvmomi','PrettyTable',
    ],
)
