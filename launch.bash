#!/usr/bin/env bash

#the git command that I have done to get refs
#git clone git://pyjs.org/git/pyjamas.git
#git clone http://git.nuitka.net/Nuitka.git
#git clone git://gitorious.org/shedskin/mainline.git
#svn checkout http://jslibs.googlecode.com/svn/trunk/ jslibs-read-only

#wget http://ftp.mozilla.org/pub/mozilla.org/js/js185-1.0.0.tar.gz
#wget ftp://ftp.mozilla.org/pub/mozilla.org/js/rhino1_7R3.zip #and here I got js.jar


#to get info from web : git pull

currentPath="$(pwd)"
pyjamasPath="../pyjamas"

cd "$pyjamasPath"
python2.5 bootstrap.py
./bin/buildout
./bin/test

#__EOF__

