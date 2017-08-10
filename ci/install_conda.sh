#!/bin/bash
set -ev
if ! [ -d "$HOME/miniconda" ]
then
  wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh
  chmod +x miniconda.sh
  "./miniconda.sh -b -f -p $HOME/miniconda"
fi

export PATH="$HOME/miniconda/bin:$PATH"
conda update --yes conda

if ! [ -d "$HOME/miniconda/envs/testenv" ]
then
  conda create --yes -n testenv python=$TRAVIS_PYTHON_VERSION
fi
