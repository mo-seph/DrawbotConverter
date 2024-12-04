import svgutils.transform as sg

from lxml import etree
import sys
from dataclasses import dataclass
import re
import svgpathtools.path as pth
from svgpathtools import svg2paths2, wsvg, svg2paths, Path
import svgpathtools.parser as prs

from drawbot_converter.transformer import SvgTransformer
from drawbot_converter.bot_setup import BotSetup, BoundingBox, Transform
from drawbot_converter.svg_utils import parse_number_units, parse_numbers_units, size_abs


'''
# Rewrite using SVGPathtools (https://pypi.org/project/svgpathtools/)
Currently falling down on some paths.

Could try: https://github.com/meerk40t/svgelements

Or their Sax parser: https://github.com/mathandy/svgpathtools/blob/master/svgpathtools/svg_io_sax.py
'''

class TransformerSVGPathTools(SvgTransformer):


    def do_transform(self,setup,infile,outfile,initial_box,trans,checkfile=None):

        paths, attributes, svg_attributes = svg2paths2(infile)
        # Apply any transforms in the SVG attributes
        paths,attributes = apply_transforms(paths,attributes)
        paths.sort(key=path_ordering)
        transform = lambda x: pth.translate(
            pth.scale(x,
                      trans.scale,
                      origin=complex(initial_box.xmin,initial_box.ymin)),
            complex(trans.x_offset,trans.y_offset))

        new_paths = [ transform(p) for p in paths ]
        attributes = [{"stroke":"#f55","stroke-width":"0.1","fill":"none"} for a in attributes]

        #paths.append(rect(initial_box))
        #attributes.append( {"stroke":"#a55","stroke-width":"1.4","fill":"none"})
        svg_attributes['width'] = f"{setup.bot_width}"
        svg_attributes['height'] = f"{setup.bot_height}"
        svg_attributes['viewBox'] = f"0 0 {setup.bot_width} {setup.bot_height}"

        #wsvg(new_paths, attributes=attributes, svg_attributes=svg_attributes, filename=outfile)
        # was just paths?
        wsvg(new_paths, attributes=attributes, svg_attributes=svg_attributes, filename=outfile)

    def get_svg_bounding_box(self,file) -> BoundingBox:
        print("Computing bounding boxes PathTools")
        return self.bounding_box(file)

    def bounding_box(self,infile,use_viewbox=False,use_hw=False):
        '''Returns xmin,ymin,xmax,ymax for bounding box of drawing:
        - if use_viewBox is set and viewBox is present, use that
        - if use_hw is set and they height+width are present (and don't contain a
        percentage spec), return 0,0,width,height.
        - Otherwise, calculate from the curves'''
        paths, attributes, svg_attributes = svg2paths2(infile)
        vbpt = bbox(paths)
        print(f"Pre Transform bounding box: {vbpt}")
        # Apply any transforms in the SVG attributes
        paths,attributes = apply_transforms(paths,attributes)
        #for p in paths:
            #print(f"Path: {p}")

        if use_viewbox and ('viewBox' in svg_attributes):
            print(f"Viewbox exists in file: {svg_attributes['viewBox']}")
            # Viewbox is xmin, ymin, width, height
            vbp = parse_numbers_units(svg_attributes['viewBox'])
            vb = BoundingBox(vbp[0], vbp[1], vbp[0]+vbp[2],vbp[1]+vbp[3])
        elif ( use_hw and svg_attributes['width'] and
                svg_attributes['height'] and
                size_abs(svg_attributes['width']) and
                size_abs(svg_attributes['height'])):
            print(f"Found height and width in drawing, using those")
            width = parse_number_units(svg_attributes['width'])
            height = parse_number_units(svg_attributes['height'])
            vb = BoundingBox(0, 0, width ,height)
        else:
            print(f"Computing bounding box from paths for {infile}")
            vb = bbox(paths)
        print(f"BoundingBox of SVG input: {vb}")
        return vb 
    def get_name(self):
        return "svgpathtools"

def path_ordering(p):
    try:
        return p.bbox()[0] + p.bbox()[1]
    except Exception as e:
        return 0

def apply_transforms(paths,attributes):
    print("Applying transforms...")
    trans = [apply_transform(p,a) for p,a in zip(paths,attributes)]
    trans = [ p for p in trans if p[0]]
    paths_t, attributes_t = [p for p, a in trans], [a for p, a in trans]
    return paths_t,attributes_t

def apply_transform(path,attributes):
    '''Uses the parsing on https://github.com/mathandy/svgpathtools/blob/master/svgpathtools/parser.py
    to create a transform from the SVG string'''
    #print(f"Transforming: {path}")
    if 'transform' in attributes:
        try:
            t_s = attributes['transform']
            # print(f"Transform string: `{t_s}`")
            t = prs.parse_transform(attributes['transform'])
            p = pth.transform(path,t)
            # print(f"Got transform: {t}")
            # print(f"New path: {p}")
            atts = attributes.copy()
            del atts['transform']
            return (p,atts)
        except e:
            print(e)
            return (None,None)
    if not good_path(path):
        return (None,None)
    return (path,attributes)



def good_path(p):
    try:
        pxmin, pxmax, pymin, pymax = p.bbox()
    except Exception:
        return False
    return True

def bbox(paths):
    xmin = float("inf")
    ymin = float("inf")
    xmax = float("-inf")
    ymax = float("-inf")
    for p in paths:
        try:
            pxmin, pxmax, pymin, pymax = p.bbox()
            xmin = min(xmin,pxmin)
            ymin = min(ymin,pymin)
            xmax = max(xmax,pxmax)
            ymax = max(ymax,pymax)
        except Exception as e:
            print(f"Bad path: {e}")
    return BoundingBox(xmin,ymin,xmax,ymax)


def rect(b:BoundingBox):
    return pth.bbox2path(b.xmin,b.xmax,b.ymin,b.ymax)


def label_setup(fig:sg.SVGFigure,setup:BotSetup,text=True):
    px = setup.paper_offset_w
    py = setup.paper_offset_h
    pxx = px + setup.paper_width
    pyy = py + setup.paper_height
    label_rect(fig,0,0,setup.bot_width,setup.bot_height,name="Bot",color="red",fill="None",inside=True,text=text)
    label_rect(fig,setup.paper_offset_w,setup.paper_offset_h,setup.paper_width,setup.paper_height,name="Paper",color="green",fill="None",text=text)
    label_rect(fig,setup.drawing_offset_w,setup.drawing_offset_h,setup.drawing_width,setup.drawing_height,name="Drawing",color="blue",fill="None",text=text)


if __name__ == '__main__':
    print("Converting SVG...")
    s = BotSetup(
        bot_width=760,
        bot_height=580,
        paper_width=584,
        paper_height=420,
        drawing_width=200,
        drawing_height=200
    ).center_paper().center_drawing()
    TransformerSVGPathTools().transform(s,"data/test/circle_5_positive_ripple_minified.svg","data/processed/circle_5_positive_ripple_minified-SVG_PATH.svg","data/check/circle_5_positive_ripple_minified-SVG_PATH.svg")
    #transform(s,"test/scrambler.svg","intermediate/scrambler_transformed.svg","check/scrambler_check.svg")
    #ransform(s,"input/circle_5_positive_ripple_minified.svg","intermediate/circ5.svg","check/circ5_check.svg")
