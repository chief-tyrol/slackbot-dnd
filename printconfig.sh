#!/usr/bin/env sh

sep() {
  echo '======================================================================================='
}


small_sep() {
  echo '--------------------'
}

nl() {
  echo ''
}

sep
sep
sep

echo 'Installed Python version:'
small_sep
python --version
nl

echo 'Installed pip version:'
small_sep
pip --version
nl

echo 'Installed Python packages:'
small_sep
pip freeze --all

sep
sep
sep