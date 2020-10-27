#! /bin/bash

if [ -z "${1}" ]
then
  echo -e "\e[1m\e[31mErreur: paramètres numéros affichettes manquants\e[0m"
  exit 1
fi

while [ 1 ]
do

  sleep 1
  for i in ${1}
  do

    echo
    echo -e "\e[1m\e[93mAffichette \e[92m${i}\e[0m"
    sudo sh -c "LD_LIBRARY_PATH=/home/traceone/lib/to1 xvfb-run -a -s '-screen 0 1280x1024x24' -f ~/.xauth_ python ${i}_*"
#    sudo sh -c "xvfb-run -a -s '-screen 0 1280x1024x24' -f ~/.xauth_ python ${i}_*"
  done
done
