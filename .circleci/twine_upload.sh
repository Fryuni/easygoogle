#!/bin/bash
set -ev

# Exit if not a tag
if [[ -z "$CIRCLE_TAG" ]]; then
  echo "This is not a release tag. Doing nothing."
  exit 0
fi

python3 -m easygoogle.config

pip3 install twine wheel

python3 setup.py sdist bdist_wheel
python -m twine upload dist/*
