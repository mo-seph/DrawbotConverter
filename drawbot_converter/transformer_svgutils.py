import svgutils.transform as sg
from lxml import etree
import sys
from dataclasses import dataclass

from drawbot_converter.transformer import SvgTransformer
from drawbot_converter.bot_setup import BotSetup, BoundingBox, Transform
from drawbot_converter.svg_utils import parse_number_units, parse_numbers_units, size_abs


class TransformerSVGUtils(SvgTransformer):
    def do_transform(self,setup,infile,outfile,initial_box:BoundingBox,trans:Transform,checkfile=None):
        # Read in the drawing
        svg = sg.fromfile(infile)
        drawing = svg.getroot()
        drawing.moveto(trans.x_offset,trans.y_offset,trans.scale)

        # Make a figure the right size for the drawbot
        width = f"{setup.bot_width}"
        height = f"{setup.bot_height}"
        fig = sg.SVGFigure(width=width,height=height)
        fig.root.set('height',height)
        fig.root.set('width',width)
        fig.append([drawing])
        fig.save(outfile)

    def get_name(self):
        return "svgutils"



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
    #transform(s,"test/scrambler.svg","output/scrambler_transformed.svg","output/scrambler_check.svg")
    TransformerSVGUtils().transform(s,"data/test/circle_5_positive_ripple_minified.svg","data/processed/circle_5_positive_ripple_minified-SVG_UTILS.svg","data/check/circle_5_positive_ripple_minified-SVG_UTILS.svg")
