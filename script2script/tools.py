"""
Tools module have helping function/classes for multi purpose
"""

import sys

def echo(fn, write=sys.stdout.write):
  """
  A logging/debugging function decorator
  @echo def toto(): => will print all input and output
  """
  import functools
  code = fn.func_code
  argcount = code.co_argcount
  argnames = code.co_varnames[:argcount]
  fn_defaults = fn.func_defaults or list()
  argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))

  def format_arg_value(arg_val):
    arg, val = arg_val
    return '%s=%r' % (arg, val)

  @functools.wraps(fn)
  def wrapped(*v, **k):
    positional = map(format_arg_value, zip(argnames, v))
    defaulted = [format_arg_value((a, argdefs[a]))
        for a in argnames[len(v):] if a not in k]
    nameless = map(repr, v[argcount:])
    keyword = map(format_arg_value, k.items())
    args = positional + defaulted + nameless + keyword
    write('%s(%s)\n' % (fn.__name__, ', '.join(args)))

    res = fn(*v, **k)
    write('%s => %s\n' % (fn.__name__, repr(res)))
    return res

  return wrapped
