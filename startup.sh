#!/bin/bash


BASE="$(dirname "$0")"

cd "${BASE}"

if [ ! -d ./venv ] ; then
    cat <<EOM
ERROR! You need to set up your venv.
please copypasta:

===
cd $BASE
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
deactivate
===

EOM

    exit 1
fi

err=0
for need in rtxmlrpc rtcontrol git
do
  which $need
  err=$(($err + $?))
done

if [ $err -gt 0 ] ; then
  echo "missing stuff"
  exit 1
fi


if [ "$1" = "fg" ] ; then
    ${BASE}/venv/bin/python3 -m flask run
else
    screen -d -m -S tiphandler ${BASE}/venv/bin/python3 -m flask run
    echo "running in screen"
fi


