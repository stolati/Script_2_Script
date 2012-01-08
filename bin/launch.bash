#!/usr/bin/env bash
set -eu

case "${1}" in

  init)
    refs="$all2all_path/refs"
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

    git_pull git://pyjs.org/git/pyjamas.git Pyjamas
    git_pull http://git.nuitka.net/Nuitka.git Nuitka
    git_pull git://gitorious.org/shedskin/mainline.git Shedskin
    echo "Pulling all2all from github"
    ( cd "$all2all_path" ; git pull ; )

    #how I got rhino
    #wget ftp://ftp.mozilla.org/pub/mozilla.org/js/rhino1_7R3.zip #and here I got js.jar

  ;;
  *)
    echo "launch.bash init #download/pull the git repository"
  ;;

esac

#__EOF__

