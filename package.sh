#!/bin/bash

export LC_ALL="C.UTF-8"
export LANG="C.UTF-8"
export FLASK_ENV="production"

pipenv lock -r > requirements.txt
pip3 install -r requirements.txt

tar_name=tam_server.tar.gz
zip_name=tam_server.zip

rm -rf build dist $tar_name $zip_name
pyinstaller server.py -F
rm requirements.txt

cp license.txt dist/license.txt
cd ./dist
mv server tam_server
tar -czvf $tar_name *
mv $tar_name ./../$tar_name