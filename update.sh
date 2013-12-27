#!/bin/bash
bumpversion minor
git push
git push --tags
python setup.py sdist
python setup.py bdist_wheel
