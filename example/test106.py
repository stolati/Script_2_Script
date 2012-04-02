#function declaration

def toto(a, b):
  c = a+b
  print c
  return c


toto(toto(3, 4), toto(5, 6))


def titi():
  print 'titi'

titi()
titi()

def recurWhile(a):
  if a <= 0: return a
  print a
  recurWhile(a-1)

recurWhile(10)

#__EOF__
