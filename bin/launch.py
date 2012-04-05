#!/usr/bin/env python
import sys, os, os.path
from getopt import getopt, GetoptError
from glob import glob
import re
import unittest
import subprocess
import traceback


def config(base_path):
  tmp = {
    'base_path':'%(base_path)s',
    'bin'      :'%(base_path)s/bin',
    'curScript':'%(base_path)s/bin/launch.py',
    'basename' :'launch.py',
    'doc'      :'%(base_path)s/doc',
    'example'  :'%(base_path)s/example',
    'lib'      :'%(base_path)s/lib',
    'refs'     :'%(base_path)s/refs',
    'code'     :'%(base_path)s/script2script',
    'main'     :'%(base_path)s/script2script/main.py',
    'test'     :'%(base_path)s/script2script/test',
    'wiki'     :'%(base_path)s/wiki',
  }
  res = {}
  for k, v in tmp.iteritems():
    res[k] = v % {'base_path':base_path}
  return res


def guessS2S_Path():
    env_name = 'script2script_path'

    #look for the path into os.environ
    if env_name in os.environ: return os.environ[env_name]

    #try to guess it from the script path
    myScriptPath = sys.argv[0] #./bin/launch.py
    return os.path.dirname(os.path.dirname(myScriptPath))


def getModule(fPath):
  fPath = os.path.abspath(fPath)
  path, name = os.path.dirname(fPath), os.path.splitext(os.path.basename(fPath))[0]

  sys_save = list(sys.path)
  if path not in sys.path: sys.path[0:0] = [path]

  res = __import__(name)

  sys.path = sys_save
  return res


def git_pull(git_path, dir_path):
  dir_name = os.path.basename(dir_path)

  if not os.path.isdir(dir_path):
    print "Cloning %s" % dir_path
    subprocess.call(['git', 'clone', dir_path], shell=True)
  else:
    print "Pulling %s" % dir_path
    cd_save = os.getcwd()
    os.chdir(dir_path)
    subprocess.call('git pull', shell=True)
    os.chdir(cd_save)


class Execute(object):

  def __init__(self, config):
    self._config = config

  def help(self, msg = None):
    def w(m): sys.stderr.write(m + "\n")

    if msg: w('!' * 30); w(msg); w('!' * 30)

    for fname in dir(self):
      if not fname.startswith('cmd_'): continue
      f = getattr(self, fname)
      w( f.__doc__ % self._config )


  def __call__(self, params):
    if len(params) == 0:
      return self.help("Not enough arguments")

    cmd = params.pop(0)
    try:
      f = getattr(self, 'cmd_%s' % cmd)
    except AttributeError:
      return self.help("Command '%s' not known" % cmd)

    try:
      f(params)
    except GetoptError:
      self.help("Command badly used")


  def cmd_help(self, params):
    """%(basename)s help #print this help"""
    self.help()

  def cmd_list(self, params):
    """%(basename)s list [-m|--main] [-t|--test] #list python files in the project, with only main code, or only tests"""
    withMain, withTest = True, True
    opts, args = getopt(params, "mt", ["main", "test"])
    if len(args) != 0: return self.help("list command don't take value arguments")

    for opt, arg in opts:
      if opt in ('-m', '--main'): withMain, withTest = True, False
      if opt in ('-t', '--test'): withMain, withTest = False, True

    codePath, testPath = os.path.abspath(self._config['code']), os.path.abspath(self._config['test'])

    for root, dirs, files in os.walk(codePath):
      isInTest = os.path.commonprefix([root, testPath]) == testPath
      if not withTest and isInTest : continue
      if not withMain and not isInTest : continue

      for name in files:
        if name == '__init__.py': continue
        if not name.endswith('.py'): continue
        filePath = os.path.join(root, name)
        print filePath


  def cmd_todo(self, params):
    """%(basename)s todo #return a list of all the todos inside the project"""
    if len(params) != 0: return self.help("todo command don't take value arguments")

    codePath = os.path.abspath(self._config['code'])
    todoRe = re.compile(".*todo.*", re.I)

    for root, dirs, files in os.walk(codePath):
      for name in files:
        if not name.endswith('.py'): continue

        filepath = os.path.join(root, name)
        trunkatedPath = '.' + filepath[len(codePath):]

        alreadyUsed = False
        with open(filepath) as f:
          for num, line in enumerate(f):
            if not todoRe.match(line): continue
            if not alreadyUsed:
              print ''
              print 'in %s :' % trunkatedPath
            print '%s %s' % (num, line),

  def cmd_tests(self, params):
    """%(basename)s tests [-a|--all] [-i|--interactive] [-y|--auto] [<num> ...] #launch main with a list of test file, or all test files, default the first one"""

    opts, args = getopt(params, "aiy", ["all", "interactive", "auto"])
    getAll = False
    for opt, arg in opts:
      if opt in ('-a', '--all'): getAll = True

    interactive =  len(args) > 1 or getAll
    for opt, arg in opts:
      if opt in ('-i', '--interactive'): interactive = True
      if opt in ('-y', '--auto'): interactive = False
    if not args : args = ['0']

    exPath = self._config['example']

    if getAll:
      files = glob('%s/*.py' % exPath)
    else:
      files = [
        sorted(glob('%s/*%s*.py' % (exPath, num)))[0]
        for num in args ]

    files.sort()

    main_module = getModule(self._config['main'])

    for f in files:
      try:
        main_module.processFile(f)
      except Exception as e:
        traceback.print_exc(file=sys.stdout)

      if interactive: raw_input()


  def cmd_test(self, params):
    """%(basename)s tests [name] #launch unittest modules"""
    opts, args = getopt(params, "v", ["verbose"])
    verboseLevel = 1
    for opt, arg in opts:
      if opt in ('-v', '--verbose'): verboseLevel += 1

    disco = unittest.defaultTestLoader.discover
    tests = []

    if args:
      for filt in args:
        tests.append(disco(self._config['test'], pattern='test*%s*.py' % filt))
    else:
      tests.append(disco(self._config['test'], pattern='test*.py'))

    testSuite = unittest.TestSuite(tests)
    testRunner = unittest.TextTestRunner(stream=sys.stdout, verbosity=verboseLevel).run
    testRunner(testSuite)


  def cmd_init(self, params):
    """%(basename)s init #download/pull the gits repositories"""
    if len(params) != 0: return self.help("init command don't take value arguments")

    git_pull('git@github.com:stolati/Script_2_Script.git', self._config['base_path'])
    git_pull('git://pyjs.org/git/pyjamas.git', self._config['refs'] + '/Pyjamas')
    git_pull('http://git.nuitka.net/Nuitka.git', self._config['refs']+ '/Nuitka')
    git_pull('git://gitorious.org/shedskin/mainline.git', self._config['refs']+ '/Shedskin')
    git_pull('git@github.com:stolati/Script_2_Script.wiki.git', self._config['wiki'])
    #mercurial_pull https://bitbucket.org/pypy/pypy "$refs/Pypy")
    #mercurial_pull https://mock.googlecode.com/hg "$refs/mock")

    #( cd "$refs/Pyjamas" ; python bootstrap.py ; )


#    echo "$launch_exe pylint #launch pylint on all the files"
#    echo "$launch_exe docs #generate documentation"



if __name__ == "__main__":
    base_path = guessS2S_Path()
    config = config(base_path)

    if base_path not in sys.path: sys.path.append(base_path)

    e = Execute(config)
    e(sys.argv[1:])
    #e(['toto'])
    #e(['help'])
    #e(['list'])
    #e(['list', '-m'])
    #e(['list', '-t'])
    #e(['todo'])
    #e(['tests', '-a'])
    #e(['tests', '-y', '1', '10'])

    #e(['test', '-v'])
    #e(['test', '-v', 'simp'])
    #e(['init'])



#
#launch_exe="$0"
#
#command="${1:-}"
#shift || true
#
#case "$command" in
#
#  init)
#    mkdir -p "$refs"
#
#    git_pull(){ #<git_path> <dir_name>
#      typeset git_path="$1" dir_name="$2"
#      if [[ ! -d "$refs/$dir_name" ]]; then
#        echo "Cloning $dir_name"
#        git clone "$git_path" "$dir_name" || true
#        return
#      fi
#
#      echo "Pulling $(basename $dir_name)"
#      (
#        cd "$dir_name"
#        git pull || true
#      )
#    }
#
#    mercurial_pull(){ #<mercurial_path> <dir_name>
#      typeset merc_path="$1" dir_name="$2"
#      [[ ! -d "$dir_name" ]] || hg clone "$merc_path" "$$dir_name"
#      echo "Pulling $dir_name"
#      (
#        cd "$dir_name"
#        #TODO search for update mercurial stuffs, I don't know how to do
#        #hg update --insecure
#      )
#    }
#
#    #echo "Pulling script2script from github"
#    #( cd "$script2script_path" ; git pull ; )
#
#    git_pull '' "$script2script_path"
#    git_pull git://pyjs.org/git/pyjamas.git "$refs/Pyjamas"
#    git_pull http://git.nuitka.net/Nuitka.git "$refs/Nuitka"
#    git_pull git://gitorious.org/shedskin/mainline.git "$refs/Shedskin"
#    git_pull git@github.com:stolati/Script_2_Script.wiki.git "$script2script_path/wiki"
#    mercurial_pull https://bitbucket.org/pypy/pypy "$refs/Pypy"
#    mercurial_pull https://mock.googlecode.com/hg "$refs/mock"
#
#    ( cd "$refs/Pyjamas" ; python bootstrap.py ; )
#
#  ;;
#
#  tests) #launch the unittest
#    if [[ "X${1:-}" = "X--loop" ]]; then
#      loop=true
#      shift
#      name="${1:-}"
#
#      echo ""
#      echo "#########################"
#      echo " Exit the loop by Ctrl-C "
#      echo "#########################"
#      echo ""
#
#      new=""
#      old="different than new"
#      while true; do
#        date
#        old="$new"
#        while [ "X$old" == "X$new" ]; do
#          sleep 1
#          new="$($launch_exe tests "$name" 2>&1 | egrep -v '^Ran [0-9]+ tests in [0-9.]+s$')"
#        done
#        echo "$new"
#      done
#
#      #exit by Ctrl-C
#    fi
#
#    (
#      name="test*${1:-}*.py"
#      cd "$test" #change in case of access by absolute
#      python -m unittest discover -s "$test" -v -p "$name"
#
#    )
#  ;;
#
#  pylint) #launch pylint on the code
#   pylint --rcfile="$script2script_path/pylint.conf" "$code"
#   #TODO idea is to use the -e arguments
#   #TODO use -d instead, some errors are no worth using
#
#  ;;
#  list)
#    filter="${1:-}"
#    find "$code" -name '*.py' | grep -v __init__ | grep -i "$filter"
#  ;;
#
#  todo)
#    (
#      cd "$script2script_path"
#      find script2script test -type f | xargs grep --color TODO
#    )
#  ;;
#  docs)
#    (
#      cd "$script2script_path"
#      rm -Rf "$script2script_path/apidoc"
#      mkdir -p "$script2script_path/apidoc"
#      epydoc --conf epydoc.conf
#      epydoc --check "script2script"
#    )
#  ;;
#  *)
#    echo "$launch_exe init #download/pull the git repository"
#    echo "$launch_exe test <num> #launch main with a test"
#    echo "$launch_exe tests [--loop] [name] #launch unittest modules"
#    echo "$launch_exe pylint #launch pylint on all the files"
#    echo "$launch_exe list #list python files in the project"
#    echo "$launch_exe todo #return a list of all the todo in files"
#    echo "$launch_exe docs #generate documentation"
#  ;;
#
#esac
#
#
##how I got rhino
##wget ftp://ftp.mozilla.org/pub/mozilla.org/js/rhino1_7R3.zip #and here I got js.jar
#
##TODO I can use the Pyjamaas/pyjs/tests as my own tests

#__EOF__

