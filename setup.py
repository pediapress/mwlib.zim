#! /usr/bin/env python

# Copyright (c) 2011 PediaPress GmbH
# See README.txt for additional licensing information.

import os
from setuptools import setup


def get_version():
    d = {}
    execfile("mwlib/zim/__init__.py", d, d)
    return d["version"]


def main():
    if os.path.exists("Makefile"):
        print 'Running make'
        os.system('make')

    setup(
        name="mwlib.zim",
        version=get_version(),
        entry_points={
            'mwlib.writers': ['zim = mwlib.zim.zimwriter:writer']},
        install_requires=['mwlib', 'pyzim>=0.3', 'lxml'],
        packages=["mwlib", "mwlib.zim"],
        namespace_packages=['mwlib'],
        zip_safe=False,
        include_package_data=True,
        url="http://code.pediapress.com/",
        description="generate zim files from mediawiki markup",
        long_description=open("README.txt").read(),
        license="BSD License",
        maintainer="pediapress.com",
        maintainer_email="info@pediapress.com")

if __name__ == '__main__':
    main()
