#!/usr/bin/env python


class Mock:

  listMock = []

  def __getattr__(self, name):
    if name in ['__iter__', '__getitem__']:
      print '__getattr__', name, ' => AttributeError'
      raise AttributeError()
    print "__getattr__ %s, %s" % (self, name)
    m = Mock()
    #listMock.append(m)
    print 'returning %s' % m
    return m

  def __call__(self, *args, **kargs):
    print "__call__", args, kargs
    return self

  def __str__(self): return '<Mock %s>' % id(self)



m = Mock()
print m
print "hello world"
i = iter(m)
print i




#def iter(el):
#  try:
#    return getattr(self, "__iter__")()
#  except AttributeError:
#    pass
#
#  try:
#    gi = getattr(self, "__getitem__")
#  except AttributeError:
#    pass
#  else:
#    return iterator_getitem(gi)
#







#__EOF__
