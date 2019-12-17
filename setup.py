import os
from setuptools import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name="gistquery",
    author="Oszkar Nagy",
    author_email="oszkar@na.gy",
    url="https://github.com/cocooma/gistquery/",
    description="Query if a specific user has a new gist available",
    long_description=read(filename='README.md'),
    license="Apache Software License (Apache 2.0)",
    platforms=["Linux", "MacOS"],
    install_requires=["pipenv", "setuptools"],
    classifiers=[
        'Development Status :: 1 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3.8.0'
    ]
)
