# pylint: disable=no-init, too-few-public-methods, old-style-class

import xml.etree.ElementTree as ET
from xml_box2d import XmlBox2D


box2d = XmlBox2D.from_xml(ET.fromstring(open("test.xml").read()))
world = box2d.to_box2d()
print world
