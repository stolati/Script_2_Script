#!/usr/bin/env bash
set -eu

refs="$all2all_path/refs"
input="$all2all_path/input"
output="$all2all_path/output"
tmp="$all2all_path/tmp"

case "${1:-}" in
  compile)
    pyjscompile="$refs/Pyjamas/bin/pyjscompile"
    pyjampiler="$refs/Pyjamas/bin/pyjampiler"
    pyjsbuild="$refs/Pyjamas/bin/pyjsbuild"
    python "$pyjsbuild" \
      --output="$output/main.js" \
      "$input/main.py"


  ;;
  init)
    mkdir -p "$refs" && cd "$refs"

    git_pull(){ #<git_path> <dir_name>
      typeset git_path="$1" dir_name="$2"
      [[ -d "$refs/$dir_name" ]] || git clone "$git_path" "$dir_name"

      echo "Pulling $dir_name"
      (
        cd "$refs/$dir_name"
        git pull
      )
    }
    mercurial_pull(){ #<mercurial_path> <dir_name>
      typeset merc_path="$1" dir_name="$2"
      [[ -d "$refs/$dir_name" ]] || hg clone --insecure "$merc_path" "$dir_name"
      echo "Pulling $dir_name"
      (
        cd "$refs/$dir_name"
        hg pull --insecure
      )
    }

    echo "Pulling all2all from github"
    ( cd "$all2all_path" ; git pull ; )

    git_pull git://pyjs.org/git/pyjamas.git Pyjamas
    git_pull http://git.nuitka.net/Nuitka.git Nuitka
    git_pull git://gitorious.org/shedskin/mainline.git Shedskin
    mercurial_pull https://bitbucket.org/pypy/pypy Pypy

    ( cd "$refs/Pyjamas" ; python bootstrap.py ; )

  ;;
  *)
    echo "launch.bash init #download/pull the git repository"
    echo "launch.bash test #compile the source, and launch it"
  ;;

esac


#how I got rhino
#wget ftp://ftp.mozilla.org/pub/mozilla.org/js/rhino1_7R3.zip #and here I got js.jar

#TODO I can use the Pyjamaas/pyjs/tests as my own tests

#__EOF__

