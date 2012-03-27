#if and conditions

a = 3
b = 4


if a == b:
  print 'a == b'
else:
  print 'a != b'
  if a < b:
    print 'a < b'


a = 3
b = 4
if a != b:
  print 'a != b'
  if not a > b:
    print 'not a > b'
else:
  print 'a == b'

