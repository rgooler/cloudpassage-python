#!/bin/bash
if [[ -z "$1" ]]; then
    PATCHLEVEL=minor
else
    PATCHLEVEL=$1
fi
bumpversion $PATCHLEVEL
git push
git push --tags
python setup.py sdist upload
python setup.py bdist_wheel upload
