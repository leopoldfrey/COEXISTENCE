#!/bin/bash

printf "\033[0m\n"
printf "local IP should be : \033[37;40m 192.168.3.11 \033[0m\n"
printf "chataigne IP should be : \033[37;40m 192.168.3.10 \033[0m\n"

ifconfig en0 | awk '$1 == "inet" {print "en0: \033[37;40m " $2 " \033[0m"}'
ifconfig en1 | awk '$1 == "inet" {print "en1: \033[37;40m " $2 " \033[0m"}'
ifconfig lo0 | awk '$1 == "inet" {print "lo0: \033[37;40m " $2 " \033[0m"}'

echo " "

cd $(dirname $0)

#echo opening LIVE SET
#open "/Users/leo/Documents/__PROJETS/_pulso/Animal/Hic Machina Project/G5 _COEX_ sept19 TNG 3.als" &
echo manually open LIVE SET

echo opening COEXISTENCE MAX PATCH
open ./COEXISTENCE_4.maxpat &

echo opening g5WebCtrl MAX PATCH
open ./g5WebCtrl/g5WebCtrl.maxpat &

echo opening WEBSITE CONTROLLER webpage
open -a "Google Chrome" http://g5interspecies.herokuapp.com/controller.html &

echo opening LITHOSYS webpage
open -a "Google Chrome" http://localhost:8080 &

echo " "

echo Starting LITHOSYS
export PYTHONPATH=:$(dirname $0)/lithosys/src/
cd $(dirname $0)/lithosys/src
python3 -W ignore ./lithosys.py

