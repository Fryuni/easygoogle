#!/bin/bash
set -ev

# Exit if not a tag
if [[ -z "$CIRCLE_TAG" ]]; then
  echo "This is not a release tag. Doing nothing."
  exit 0
fi

python3 -m easygoogle.config

pip3 install -IU twine wheel

python3 setup.py sdist
python3 setup.py bdist_wheel --universal
python -m twine upload dist/*
