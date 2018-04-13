
class ParameterNode(object):
  def __init__(self, children):
    self.children = children

class ParameterNodeAtInstant(object):
  def __init__(self, node, instant):
      for child_name, child in node.children.items():
        setattr(self, child_name, PlaceHolder(child, instant))

  def __getattribute__(self, name):
    attribute = object.__getattribute__(self, name)

    if not isinstance(attribute, PlaceHolder):
      return attribute

    attribute = attribute.resolve()
    setattr(self, name, attribute)

    return attribute

class PlaceHolder(object):
  def __init__(self, child, instant):
    self.child = child
    self.instant = instant

  def resolve(self):
    print('Resolving {} for intant {}'.format(self.child.name, self.instant))
    return self.child.get_at_instant(self.instant)

class Child(object):
  def __init__(self, name):
    self.name = name

  def get_at_instant(self, instant):
    return u'{}:{}'.format(self.name, instant)


node = ParameterNode({'rsa': Child('rsa'), 'cmu': Child('cmu')})

node_at_instant = ParameterNodeAtInstant(node, '2018')

# assert node_at_instant.cmu == 'cmu:2018'
