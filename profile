#!/usr/bin/env bash

export script2script_path="$PWD"
PATH="$PATH:$script2script_path/bin"

lib_path="$script2script_path/lib"
export PYTHONPATH="$PYTHONPATH:$script2script_path:$lib_path/mock"




#__EOF__

