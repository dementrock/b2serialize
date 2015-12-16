# pylint: disable=no-init, too-few-public-methods, old-style-class

import numpy as np


class Type(object):

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def from_str(self, s):
        raise NotImplementedError


class Float(Type):

    def from_str(self, s):
        return float(eval(s))


class Int(Type):

    def from_str(self, s):
        return int(eval(s))


class Hex(Type):

    def from_str(self, s):
        assert s.startswith("0x") or s.startswith("0X")
        return int(s, 16)


class Choice(Type):

    def __init__(self, *options):
        self._options = options

    def from_str(self, s):
        if s in self._options:
            return s
        raise ValueError("Unexpected value %s: must be one of %s" %
                         (s, ", ".join(self._options)))


class List(Type):

    def __init__(self, elem_type):
        self.elem_type = elem_type

    def __eq__(self, other):
        return self.__class__ == other.__class__ \
            and self.elem_type == other.elem_type

    def from_str(self, s):
        if ";" in s:
            segments = s.split(";")
        elif "," in s:
            segments = s.split(",")
        else:
            segments = s.split(" ")
        return map(self.elem_type.from_str, segments)


class Tuple(Type):

    def __init__(self, *elem_types):
        self.elem_types = elem_types

    def __eq__(self, other):
        return self.__class__ == other.__class__ \
            and self.elem_types == other.elem_types

    def from_str(self, s):
        if ";" in s:
            segments = s.split(";")
        elif "," in s:
            segments = s.split(",")
        else:
            segments = s.split(" ")
        if len(segments) != len(self.elem_types):
            raise ValueError(
                "Length mismatch: expected a tuple of length %d" %
                len(self.elem_types))
        return tuple([typ.from_str(seg)
                      for typ, seg in zip(self.elem_types, segments)])


class String(Type):

    def from_str(self, s):
        return s


class Angle(Type):

    def from_str(self, s):
        if s.endswith("deg"):
            return float(s[:-len("deg")]) * np.pi / 180.0
        elif s.endswith("rad"):
            return float(s[:-len("rad")])
        return float(s)

Point2D = lambda: Tuple(Float(), Float())
