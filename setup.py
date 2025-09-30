# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = "1.1.0"

setup(
  name="senaite.registries",
  version=version,
  description="Registries management add-on for SENAITE LIMS",
  long_description=open("README.rst").read() if hasattr(open, '__call__') else "",
  classifiers=[
    "Framework :: Plone",
    "Framework :: Zope2",
    "Programming Language :: Python",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
  ],
  keywords=["senaite", "lims", "registries"],
  author="Open Source Contributor",
  author_email="info@senaite.com",
  url="https://github.com/halsbox/senaite.registries",
  license="GPLv2",
  packages=find_packages("src", exclude=["ez_setup"]),
  package_dir={"": "src"},
  namespace_packages=["senaite"],
  include_package_data=True,
  zip_safe=False,
  install_requires=[
    "senaite.core>=2.6.0"
  ],
  entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
