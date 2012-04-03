#!/usr/bin/env bash

#!!! only work under unix !!!

arg="${1:-101}"

filePatt="test*${arg:-}*.py"
base_path="$(dirname "$(dirname $0)")/example"

file="$(find "$base_path" -name "$filePatt" | sort | head -1)"

res_Python="$(python $file)"

launch_res="$(launch tests $arg)"

#filter the result
place_from_begin="$(echo "$launch_res" | grep -n '//' | cut -d: -f1 | head -1)"
place_from_end=$(expr "$(echo "$launch_res" | wc -l | xargs)" - $place_from_begin + 1)
code_Js="$(echo "$launch_res" | tail -n -$place_from_end)"


tmpFile="/tmp/$RANDOM.testJs.js"
echo "$code_Js" > $tmpFile


res_Js="$(rhino "$tmpFile")"


echo "$code_Js"
echo
echo
echo Python :
echo "$res_Python"
echo
echo Javascript :
echo "$res_Js"
echo

if [[ "$res_Python" = "$res_Js" ]]; then
  echo "all is ok"
else
  echo "!!!!!! KO KO KO !!!!!!"
fi


rm "$tmpFile"


#__EOF__
