#!/bin/bash
if [[ -z "$1" ]]; then
    PATCHLEVEL=$1
else
    PATCHLEVEL=minor
fi
bumpversion $PATCHLEVEL
git push
git push --tags
python setup.py sdist upload
python setup.py bdist_wheel upload
