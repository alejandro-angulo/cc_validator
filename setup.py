import os
from setuptools import find_packages, setup
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='cc_validator',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    description='A Django app to to validate and generate credit/debit card numbers.',
    long_description=README,
    author='Alejandro Angulo',
    author_email='alejandro.b.angulo@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
)