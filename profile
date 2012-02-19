#!/usr/bin/env bash

export all2all_path="$PWD"
PATH="$PATH:$all2all_path/bin"

lib_path="$all2all_path/lib"
export PYTHONPATH="$PYTHONPATH:$all2all_path/code:$lib_path/mock"




#__EOF__

