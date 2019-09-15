#!/bin/bash
set -ev

# Exit if not a tag
if [[ -z "$CIRCLE_TAG" ]]; then
  echo "This is not a release tag. Doing nothing."
  exit 0
fi

#python -m easygoogle.config

pip install -IU twine wheel

python setup.py sdist
python setup.py bdist_wheel --python-tag py3.6
python -m twine upload dist/*
