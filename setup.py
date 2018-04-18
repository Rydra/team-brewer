#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='pairs',
      version='1',
      description='',
      url='https://github.com/Rydra/random_pairs',
      author='David Jiménez (Rydra)',
      author_email='davigetto@gmail.com',
      license='MIT',
      keywords='',
      packages=find_packages(),
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
      ],
      install_requires=['slackclient'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      include_package_data=True,
      zip_safe=False)
