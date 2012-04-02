#function declaration


class Toto:

  def __init__(self):
    self.tutu = 3
    print self.tutu

  def titi(self, tutu):
    self.tutu = tutu
    return self

  def toto(self, tralala):
    print self.tutu + tralala


a = Toto()
a.titi(4)
a.toto(5)

Toto().toto(10)
#Toto().titi(100).toto(10)


#__EOF__
