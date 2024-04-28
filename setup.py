"""Setup script for leafspy"""

from setuptools import setup, find_packages

name = "leafspy"
description = "Data conversion for Leafs."
version = "0.2.0"

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

included_packages = find_packages(exclude=["build", "docs", "templates"])

requirements = ["flask", "cellpy>=1.0.1", "galvani", "werkzeug", "psycopg2"]

test_requirements = requirements + [
    "black",
    "pytest",
]

setup(
    name=name,
    version=version,
    description=description,
    long_description=readme + "\n\n" + history,
    url="https://github.com/energycombined/leafs",
    author="energycombined",
    author_email="t.vandijk@uniresearch.com",
    license="MIT",
    packages=included_packages,
    install_requires=requirements,
    zip_safe=False,
    keywords="leafspy",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    test_suite="tests",
    tests_require=test_requirements,
)
