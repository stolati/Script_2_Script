#function declaration


class Toto:

  def __init__(self):
    self.tutu = 3
    print self.tutu

  def titi(self, tutu):
    self.tutu = tutu
    return self

  def tata(self):
    return self.tutu

  def toto(self, tralala):
    print self.tutu + tralala


a = Toto()
a.titi(40)

b = Toto()
print b.tata()

#Toto().toto(10)
#Toto().titi(100).toto(10)


#__EOF__
