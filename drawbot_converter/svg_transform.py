import svgutils.transform as sg
from lxml import etree
import sys
from dataclasses import dataclass
import re

@dataclass
class BotSetup:
    bot_width:float
    bot_height:float
    paper_width:float
    paper_height:float
    drawing_width:float
    drawing_height:float
    paper_offset_w:float = 0
    paper_offset_h:float = 0
    drawing_offset_w:float = 0
    drawing_offset_h:float = 0

    def center_paper(self):
        self.paper_offset_w = (self.bot_width - self.paper_width)/2
        self.paper_offset_h = (self.bot_height - self.paper_height)/2
        return self

    def center_drawing(self):
        self.drawing_offset_w = self.paper_offset_w + (self.paper_width - self.drawing_width)/2
        self.drawing_offset_h = self.paper_offset_h + (self.paper_height - self.drawing_height)/2
        return self


def rect(x,y,w,h,width=1,color="black",fill="none"):
    points =[[x,y],[x+w,y],[x+w,y+h],[x,y+h],[x,y]]
    rect= sg.LineElement(points,width,color)
    rect.root.attrib['fill'] = fill
    return rect

def label_rect(fig,x,y,w,h,color="black",fill="none",name="",inside=False,text=True):
    top_offset = -3
    bottom_offset = 13
    if inside:
        top_offset = 13
        bottom_offset = -3
    fig.append([
        rect(x,y,w,h,width=1,color=color,fill=fill),
    ])
    if text:
        fig.append([
            sg.TextElement(x,y+top_offset, f"{name}: ({x},{y})", size=12, weight="bold"),
            sg.TextElement(x+w,y+h+bottom_offset, f"({x+w},{y+h})", size=12, weight="bold",anchor="end"),
        ] )


def transform(setup,infile,outfile,checkfile=None):
    width = f"{setup.bot_width}"
    height = f"{setup.bot_height}"
    fig = sg.SVGFigure(width=width,height=height)
    print(f"Width: {setup.bot_width}")
    print(f"Fig: {fig}")
    fig.root.set('height',height)
    fig.root.set('width',width)
    svg = sg.fromfile(infile)
    drawing = svg.getroot()
    scale,x,y = get_placement(setup,svg)

    drawing.moveto(x,y,scale)
    fig.append([drawing])
    fig.save(outfile)

    if checkfile:
        label_setup(fig,setup,text=False)
        fig.save(checkfile)

def get_placement(setup,image):
    x_offset = 0
    y_offset = 0
    if image.width:
        img_w =float(re.sub("[^\d\.]", "", image.width) )
        img_h =float(re.sub("[^\d\.]", "", image.height) )
    else:
        print(f"Image: {image}")
        print(f"Viewbox: {image.root.get('viewBox')}")
        vb = image.root.get('viewBox')
        box = [ float(re.sub("[^\d\.-]", "", x) ) for x in vb.split()]
        img_w = box[2]-box[0]
        img_h = box[3] - box[1]
        x_offset = -box[0]
        y_offset = -box[1]

    width_scale = setup.drawing_width / img_w
    height_scale = setup.drawing_height / img_h

    scale = min(width_scale,height_scale)
    place_x = setup.drawing_offset_w + (x_offset*scale)
    place_y = setup.drawing_offset_h + (y_offset*scale)

    if width_scale > height_scale: #Then the drawing will touch top and bottom of box
        place_x = setup.drawing_offset_w + (x_offset*scale) + (setup.drawing_width-(img_w * height_scale))/2
    else:
        place_y = setup.drawing_offset_h + (y_offset*scale)+ (setup.drawing_height -(img_h * width_scale))/2
    return scale, place_x, place_y



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
    #transform(s,"test/scrambler.svg","output/scrambler_transformed.svg","output/scrambler_check.svg")
    transform(s,"input/circle_5_positive_ripple_minified.svg","intermediate/circ5.svg","check/circ5_check.svg")
