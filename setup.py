import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-ext_fields',
    version='1.2.1',
    packages=['ext_fields'],
    include_package_data=True,
    license='MIT License',  # example license
    description='Helper decorator to create models that can contains dynamic fields',
    long_description=README,
    url='http://github.com/humantech/django-ext_fields',
    author='Humantech',
    author_email='jean.schmidt@humantech.com.br',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
)