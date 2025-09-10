#! /usr/bin/env bash

set -e

python -m build
twine upload dist/*

VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")

git tag -a "v$VERSION" -m "Release v$VERSION"
git push origin "v$VERSION"
