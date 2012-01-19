#!/usr/bin/env bash
set -eu

if [[ -z "${all2all_path:-}" ]]; then
  echo "Profile not loaded"
  echo ". profile"
  exit 1
fi

refs="$all2all_path/refs"
input="$all2all_path/input"
output="$all2all_path/output"
tmp="$all2all_path/tmp"

command="${1:-}"
shift || true

case "$command" in

  test) #launch main with a test
    testNum="${1:-}"
    listTests(){ #<filtre>
      ls "$all2all_path/tests" | grep '.py$' | grep "${1:-}" | head -1
    }
    file="$(listTests "$testNum")"
    "$all2all_path/all2all/main.py" "$all2all_path/tests/$file"
  ;;
  compile)
    pyjscompile="$refs/Pyjamas/bin/pyjscompile"
    pyjampiler="$refs/Pyjamas/bin/pyjampiler"
    pyjsbuild="$refs/Pyjamas/bin/pyjsbuild"
    python "$pyjsbuild" \
      --output="$output/main.js" \
      "$input/main.py"


  ;;
  init)
    mkdir -p "$refs"

    git_pull(){ #<git_path> <dir_name>
      typeset git_path="$1" dir_name="$2"
      [[ -d "$refs/$dir_name" ]] || git clone "$git_path" "$refs/$dir_name"

      echo "Pulling $dir_name"
      (
        cd "$refs/$dir_name"
        git pull
      )
    }
    mercurial_pull(){ #<mercurial_path> <dir_name>
      typeset merc_path="$1" dir_name="$2"
      [[ -d "$refs/$dir_name" ]] || hg clone "$merc_path" "$refs/$dir_name"
      echo "Pulling $dir_name"
      (
        cd "$refs/$dir_name"
        #TODO search for update mercurial stuffs, I don't know how to do
        #hg update --insecure
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
    echo "launch.bash test <num> #launch main with a test"
  ;;

esac


#how I got rhino
#wget ftp://ftp.mozilla.org/pub/mozilla.org/js/rhino1_7R3.zip #and here I got js.jar

#TODO I can use the Pyjamaas/pyjs/tests as my own tests

#__EOF__

