"""degoogle setup."""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name="degoogle",
                 version="1.0.1",
                 author="deepseagirl",
                 description=("Search and extract google results."),
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url="https://github.com/deepseagirl/degoogle",
                 packages=setuptools.find_packages(),
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "Operating System :: OS Independent",
                 ],
                 python_requires='>=3.6',
                 install_requires=[
                     "requests"
                 ],
                 entry_points={
                     'console_scripts': ['degoogle=degoogle.degoogle:main'],
                 })
