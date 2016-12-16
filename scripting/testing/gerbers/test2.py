#! /usr/bin/env python
import cairo
from math import pi
import sys

width = 200
height = 100

surface = cairo.SVGSurface('file.svg',width,height)
cr = cairo.Context(surface)

cr.scale(width,height)

cr.set_line_width(0.01)

cr.save()
