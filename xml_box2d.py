# pylint: disable=no-init, too-few-public-methods, old-style-class

import xml.etree.ElementTree as ET
from xml_elem import XmlElem, XmlChild, XmlAttr, XmlChildren
from xml_attr_types import Tuple, Float, Choice, String, List, Point2D, Hex, \
    Int, Angle
import Box2D


class XmlBox2D(XmlElem):

    tag = "box2d"

    class Meta:
        world = XmlChild("world", lambda: XmlWorld, required=True)

    def __init__(self):
        self.world = None

    def to_box2d(self):
        return self.world.to_box2d()


class XmlWorld(XmlElem):

    tag = "world"

    class Meta:
        bodies = XmlChildren("body", lambda: XmlBody)
        gravity = XmlAttr("gravity", Point2D())
        joints = XmlChildren("joint", lambda: XmlJoint)

    def __init__(self):
        self.bodies = []
        self.gravity = None
        self.joints = []

    def to_box2d(self):
        world = Box2D.b2World(allow_sleeping=False)
        if self.gravity:
            world.gravity = self.gravity
        for body in self.bodies:
            body.to_box2d(world, self)
        for joint in self.joints:
            joint.to_box2d(world, self)
        return world


class XmlBody(XmlElem):

    tag = "body"

    TYPES = ["static", "kinematic", "dynamic"]

    class Meta:
        color = XmlAttr("color", List(Float()))
        name = XmlAttr("name", String())
        typ = XmlAttr("type", Choice("static", "kinematic", "dynamic"),
                      required=True)
        fixtures = XmlChildren("fixture", lambda: XmlFixture)
        position = XmlAttr("position", Point2D())

    def __init__(self):
        self.color = None
        self.name = None
        self.typ = None
        self.position = None
        self.fixtures = []

    def to_box2d(self, world, xml_world):
        body = world.CreateBody(type=self.TYPES.index(self.typ))
        body.userData = dict(
            name=self.name,
            color=self.color,
        )
        if self.position:
            body.position = self.position
        for fixture in self.fixtures:
            fixture.to_box2d(body, self)
        return body


class XmlFixture(XmlElem):

    tag = "fixture"

    class Meta:
        shape = XmlAttr("shape",
                        Choice("polygon", "circle", "edge"), required=True)
        vertices = XmlAttr("vertices", List(Point2D()))
        box = XmlAttr("box", Point2D())
        radius = XmlAttr("radius", Float())
        width = XmlAttr("width", Float())
        center = XmlAttr("center", Point2D())
        angle = XmlAttr("angle", Angle())
        position = XmlAttr("position", Point2D())
        friction = XmlAttr("friction", Float())
        density = XmlAttr("density", Float())
        category_bits = XmlAttr("category_bits", Hex())
        mask_bits = XmlAttr("mask_bits", Hex())
        group_index = XmlAttr("group_index", Int())

    def __init__(self):
        self.shape = None
        self.vertices = None
        self.box = None
        self.friction = None
        self.density = None
        self.category_bits = None
        self.mask_bits = None
        self.group_index = None
        self.radius = None
        self.width = None
        self.center = None
        self.angle = None

    def to_box2d(self, body, xml_body):
        attrs = dict()
        if self.friction:
            attrs["friction"] = self.friction
        if self.density:
            attrs["density"] = self.density
        if self.group_index:
            attrs["groupIndex"] = self.group_index
        if self.radius:
            attrs["radius"] = self.radius
        if self.shape == "polygon":
            if self.box:
                fixture = body.CreatePolygonFixture(
                    box=self.box, **attrs)
            else:
                fixture = body.CreatePolygonFixture(
                    vertices=self.vertices, **attrs)
        elif self.shape == "edge":
            fixture = body.CreateEdgeFixture(vertices=self.vertices, **attrs)
        elif self.shape == "circle":
            if self.center:
                attrs["pos"] = self.center
            fixture = body.CreateCircleFixture(**attrs)
        else:
            assert False
        return fixture


def _get_name(x):
    if isinstance(x.userData, dict):
        return x.userData.get('name')
    return None


def find_body(world, name):
    return [body for body in world.bodies if _get_name(body) == name][0]


def find_joint(world, name):
    return [joint for joint in world.joints if _get_name(joint) == name][0]


class XmlJoint(XmlElem):

    tag = "joint"

    JOINT_TYPES = {
        "revolute": Box2D.b2RevoluteJoint
    }

    class Meta:
        bodyA = XmlAttr("bodyA", String(), required=True)
        bodyB = XmlAttr("bodyB", String(), required=True)
        anchor = XmlAttr("anchor", Tuple(Float(), Float()))
        anchorA = XmlAttr("anchorA", Tuple(Float(), Float()))
        anchorB = XmlAttr("anchorB", Tuple(Float(), Float()))
        lower_angle = XmlAttr("lower_angle", Angle())
        upper_angle = XmlAttr("upper_angle", Angle())
        typ = XmlAttr("type", Choice("revolute"), required=True)
        name = XmlAttr("name", String())
        angular_damping = XmlAttr("angular_damping", Float())
        linear_damping = XmlAttr("linear_damping", Float())

    def __init__(self):
        self.bodyA = None
        self.bodyB = None
        self.anchor = None
        self.anchorA = None
        self.anchorB = None
        self.lower_angle = None
        self.upper_angle = None
        self.typ = None
        self.name = None
        self.angular_damping = None
        self.linear_damping = None

    def to_box2d(self, world, xml_world):
        bodyA = find_body(world, self.bodyA)
        bodyB = find_body(world, self.bodyB)
        args = dict()
        if self.typ == "revolute":
            if self.anchor:
                args["anchor"] = self.anchor
            if self.anchorA:
                args["anchorA"] = self.anchorA
            if self.anchorB:
                args["anchorB"] = self.anchorB
            if self.lower_angle or self.upper_angle:
                args["enableLimit"] = True
            if self.lower_angle:
                args["lowerAngle"] = self.lower_angle
            if self.upper_angle:
                args["upperAngle"] = self.upper_angle
            if self.linear_damping:
                args["linearDamping"] = self.linear_damping
            if self.angular_damping:
                args["angularDamping"] = self.angular_damping

        # args["motorEnabled"] = True
        # args["motorSpeed"] = 1
        # args["maxMotorTorque"] = 1000

        joint = world.CreateJoint(type=self.JOINT_TYPES[self.typ],
                                  bodyA=bodyA,
                                  bodyB=bodyB,
                                  **args)
        # joint.motorEnabled = True
        # joint.motorSpeed = 100
        # joint.maxMotorTorque = 100000

        joint.userData = dict(
            name=self.name,
        )
        return joint


def world_from_xml(s):
    box2d = XmlBox2D.from_xml(ET.fromstring(s))
    return box2d.to_box2d()
