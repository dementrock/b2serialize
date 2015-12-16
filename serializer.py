import xml.etree.ElementTree as ET
#import lxml.etree as etree
from StringIO import StringIO
import Box2D

_default_world = Box2D.b2World()
_default_body = _default_world.CreateBody()
_default_fixture = _default_body.CreateCircleFixture()


def to_str(obj):
    if isinstance(obj, Box2D.b2Vec2):
        return ",".join("%g" % x for x in obj)
    elif isinstance(obj, tuple):
        return ",".join("%g" % x for x in obj)
    elif isinstance(obj, list):
        return ";".join(map(to_str, obj))
    else:
        raise NotImplementedError


def from_str(s, type):
    if type == "tuple":
        return tuple(map(float, s.split(",")))
    elif type == "list(tuple)":
        return [from_str(seg, "tuple") for seg in s.split(";")]
    elif type == "maybe_hex":
        if s.startswith("0x") or s.startswith("0X"):
            return int(s, 16)
        else:
            return int(s)
    else:
        raise NotImplementedError


def get_name(x):
    if isinstance(x.userData, dict):
        return x.userData.get('name')
    return None


def is_vec_equal(x, y, tolerance=1e-6):
    return all([abs(xi - yi) < tolerance for xi, yi in zip(x, y)])


def find_body(world, name):
    return [body for body in world.bodies if get_name(body) == name][0]


BODY_TYPE_STRS = ["static", "kinematic", "dynamic"]
JOINT_TYPE_STRS = ["revolute"]
JOINT_TYPES = [Box2D.b2RevoluteJoint]


def to_xml(world):
    xml_root = ET.Element('box2d')
    xml_world = ET.SubElement(xml_root, 'world')
    if world.gravity != _default_world.gravity:
        xml_world.attrib["gravity"] = to_str(world.gravity)
    for body in world.bodies:
        xml_body = ET.SubElement(xml_world, 'body')
        if 0 <= body.type and body.type < len(BODY_TYPE_STRS):
            xml_body.attrib["type"] = BODY_TYPE_STRS[body.type]
        else:
            raise ValueError("Unknown body type: %d" % body.type)
        if body.userData:
            if 'color' in body.userData:
                xml_body.attrib["color"] = to_str(body.userData["color"])
            if 'name' in body.userData:
                xml_body.attrib["name"] = body.userData["name"]
        if not is_vec_equal(body.position, _default_body.position):
            xml_body.attrib["position"] = to_str(body.position)
        for fixture in body.fixtures:
            xml_fixture = ET.SubElement(xml_body, 'fixture')
            shape = fixture.shape
            if isinstance(shape, Box2D.b2PolygonShape):
                xml_fixture.attrib["shape"] = "polygon"
                xml_fixture.attrib["vertices"] = to_str(shape.vertices)
            if fixture.friction != _default_fixture.friction:
                xml_fixture.attrib["friction"] = \
                    "%g" % fixture.friction
            if fixture.density != _default_fixture.density:
                xml_fixture.attrib["density"] = \
                    "%g" % fixture.density
            if fixture.restitution != _default_fixture.restitution:
                xml_fixture.attrib["restitution"] = \
                    "%g" % fixture.restitution
            xml_fixture.attrib["category_bits"] = \
                "0x%04X" % fixture.filterData.categoryBits
            xml_fixture.attrib["mask_bits"] = \
                "0x%04X" % fixture.filterData.maskBits
            xml_fixture.attrib["group_index"] = \
                "%d" % fixture.filterData.groupIndex
    for joint in world.joints:
        xml_joint = ET.SubElement(xml_world, 'joint')
        if not get_name(joint.bodyA):
            raise ValueError("bodyA of Joint %s does not have a name")
        if not get_name(joint.bodyB):
            raise ValueError("bodyB of Joint %s does not have a name")
        xml_joint.attrib["bodyA"] = get_name(joint.bodyA)
        xml_joint.attrib["bodyB"] = get_name(joint.bodyB)
        if is_vec_equal(joint.anchorA, joint.anchorB):
            xml_joint.attrib["anchor"] = to_str(joint.anchorA)
        else:
            xml_joint.attrib["anchorA"] = to_str(joint.anchorA)
            xml_joint.attrib["anchorB"] = to_str(joint.anchorB)
    s = ET.tostring(xml_root)
    return s#etree.tostring(etree.parse(StringIO(s)), pretty_print=True)


class Type(object):
    pass


class Float(Type):
    pass


class List(Type):

    def __init__(self, elem_type):
        self.elem_type = elem_type


class String(Type):
    pass


class WorldElem(object):
    pass


class BodyElem(object):

    class Attr:
        color = List(Float)
        name = String()
        Type = String()
    pass


class FixtureElem(object):
    pass


XML_MAP = {
    "world": WorldElem,
    "body": BodyElem,
    "fixture": FixtureElem,
}

def from_xml(s, world=None):
    xml_root = ET.fromstring(s)
    assert xml_root.tag == "box2d"
    assert len(xml_root) == 1
    xml_world = xml_root[0]
    assert xml_world.tag == "world"
    if not world:
        world = Box2D.b2World()
    if "gravity" in xml_world.attrib:
        gravity = from_str(xml_world.attrib["gravity"], "tuple")
        world.gravity = gravity
    # process all the bodies before processing any joints
    for elem in xml_world:
        if elem.tag == "body":
            xml_body = elem
            type_idx = BODY_TYPE_STRS.index(xml_body.attrib["type"])
            if type_idx < 0:
                raise NotImplementedError
            body = world.CreateBody(type=type_idx)
            userData = dict()
            if "name" in xml_body.attrib:
                userData["name"] = xml_body.attrib["name"]
            if "color" in xml_body.attrib:
                userData["color"] = from_str(xml_body.attrib["color"], "tuple")

            if len(userData) > 0:
                body.userData = userData

            if "position" in xml_body.attrib:
                body.position = from_str(xml_body.attrib["position"], "tuple")

            for xml_fixture in xml_body:
                assert xml_fixture.tag == "fixture"
                vs = from_str(xml_fixture.attrib["vertices"], "list(tuple)")

                w = max([x[0] for x in vs])
                h = max([x[1] for x in vs])
                attrs = {}
                if "restitution" in xml_fixture.attrib:
                    attrs["restitution"] = float(xml_fixture.attrib["restitution"])
                if "density" in xml_fixture.attrib:
                    attrs["density"] = float(xml_fixture.attrib["density"])
                if "friction" in xml_fixture.attrib:
                    attrs["friction"] = float(xml_fixture.attrib["friction"])
                if "category_bits" in xml_fixture.attrib:
                    attrs["categoryBits"] = \
                        from_str(xml_fixture.attrib["category_bits"], "maybe_hex")
                if "mask_bits" in xml_fixture.attrib:
                    attrs["maskBits"] = \
                        from_str(xml_fixture.attrib["mask_bits"], "maybe_hex")
                if "group_index" in xml_fixture.attrib:
                    attrs["groupIndex"] = \
                        from_str(xml_fixture.attrib["group_index"], "maybe_hex")

                if xml_fixture.attrib["shape"] == "polygon":
                    fixture = body.CreatePolygonFixture(box=(w, h), **attrs)
                else:
                    raise NotImplementedError
                if "vertices" in xml_fixture.attrib:
                    fixture.shape.vertices = from_str(xml_fixture.attrib["vertices"], "list(tuple)")
    for elem in xml_world:
        if elem.tag == "joint":
            type_idx = JOINT_TYPE_STRS.index(elem.attrib["type"])
            if type_idx < 0:
                raise NotImplementedError
            bodyA = find_body(world, elem.attrib["bodyA"])
            bodyB = find_body(world, elem.attrib["bodyB"])
            anchor = from_str(elem.attrib["anchor"], "tuple")
            joint = world.CreateJoint(type=JOINT_TYPES[type_idx], bodyA=bodyA, bodyB=bodyB, anchor=anchor)
    return world
