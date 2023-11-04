from setuptools import setup, find_packages
import os

version = os.environ.get('VERSION')
print(version)
setup(
    name='hklh_quote_api_py',
    version=version,
    packages=find_packages(),
    install_requires=[
        'protobuf>=3.20.1'
    ],
)
