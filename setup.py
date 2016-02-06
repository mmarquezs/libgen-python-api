"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from setuptools import setup, find_packages
from codecs import open
from os import path
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='libgenapi',
    version='1.0.4',
    description='Library to search on Library genesis',
    long_description=long_description,
    url='https://github.com/mmarquezs/libgen-python-api/',
    author='Marc Marquez Santamaria',
    author_email='mmsa1994@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='libgen search crawl development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    # py_modules=["libgenapi"],
    install_requires=['grab'],
)
