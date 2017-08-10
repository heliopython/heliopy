#!/bin/bash
set -ev
if not [ -d "$HOME/miniconda" ]
then
  wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh
  chmod +x miniconda.sh
  "./miniconda.sh -b -f -p $HOME/miniconda"
  export PATH="$HOME/miniconda/bin:$PATH"
fi
