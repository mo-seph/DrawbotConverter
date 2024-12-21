import drawbot_converter.svgcode as sgc
import drawbot_converter.gcode_check as gcc
import svgutils.transform as sg
import re

from drawbot_converter.bot_setup import BotSetup, BoundingBox
from drawbot_converter.svg_utils import parse_number_units, parse_numbers_units, size_abs

import pathlib
import traceback



class SvgTransformer:
    
    '''
    Transforms SVG file into GCode file, and optionally creates check files
    '''
    def pipeline(self,setup,input_svg,processed_svg,output_gcode,
                 check_svg=None,check_gcode=None,annot_check_gcode=None,
                 do_transform=True,do_gcode=True,do_check=True):
        try:
            if do_transform:
                self.transform(setup,input_svg,processed_svg,check_svg)
            if do_gcode:
                if output_gcode:
                    sgc.to_gcode(processed_svg,output_gcode)
            if do_check:
                if check_gcode:
                    gcc.gcode_to_svg(output_gcode,check_gcode,width=setup.bot_width,height=setup.bot_height)
                if annot_check_gcode:
                    self.annotate_svg(setup,check_gcode,annot_check_gcode,text=True)
        except Exception as e:
            print(f"Couldn't process path {input_svg}:\n{e}")
            traceback.print_exc()        

    """
    Transform infile (SVG) into outfile (SVG), creating checkfile (SVG) if requested

    Mostly just translates the input SVG into the right rectangle for the target machine
    """
    def transform(self,setup,infile,outfile,checkfile=None):
        drawing_box = setup.drawing_box()
        print(f"Bounding rectangle for drawing: {drawing_box}")
        initial_box = self.get_svg_bounding_box(infile)
        print(f"Bounding box of SVG input file: {initial_box}")
        if setup.fill_target:
            fitted_box = initial_box.fill_target(drawing_box)
        else:
            fitted_box = initial_box.place_inside(drawing_box)
        print(f"Target box for SVG on drawbot: {fitted_box}")
        trans = initial_box.translate_to(fitted_box)
        print(f"=> {trans}")
        self.do_transform(setup,infile,outfile,initial_box,trans)
        if checkfile:
            self.annotate_svg(setup,outfile,checkfile,text=False)
        
    
    def do_transform(self,setup,infile,outfile,initial_box,trans,checkfile=None):
        print("Not defined yet!")

    def get_svg_bounding_box(self,file) -> BoundingBox:
        image = sg.fromfile(file)
        x_offset = 0
        y_offset = 0
        vb = image.root.get('viewBox')
        if vb:
            print(f"Viewbox: {image.root.get('viewBox')}")
            box = [ float(re.sub("[^\\d\\.-]", "", x) ) for x in vb.split()]
            return BoundingBox(box[0],box[1],box[2],box[3])
        elif image.width:
            img_w =float(re.sub("[^\\d\\.]", "", image.width) )
            img_h =float(re.sub("[^\\d\\.]", "", image.height) )
        return BoundingBox(x_offset,y_offset,x_offset+img_w,y_offset+img_h)

    """
    Converts the given SVG file into a GCode file
    """
    def to_gcode(self, processed,gcode):
        sgc.to_gcode(processed,gcode)
    
    """
    Regenerates an SVG file from the given GCode file
    """
    def regen_svg_from_gcode(self,setup,gcode,check_gcode):
        gcc.gcode_to_svg(gcode,check_gcode,width=setup.bot_width,height=setup.bot_height)
    
    def annotate_svg(self,setup,original,annotated,text=True):
        svg = sg.fromfile(original)
        self.label_setup(svg,setup,text=text)
        svg.save(annotated)
    

    def label_setup(self,fig:sg.SVGFigure,setup:BotSetup,text=True):
        px = setup.paper_offset_w
        py = setup.paper_offset_h
        pxx = px + setup.paper_width
        pyy = py + setup.paper_height
        self.label_rect(fig,0,0,setup.bot_width,setup.bot_height,name="Bot",color="red",fill="None",inside=True,text=text)
        self.label_rect(fig,setup.paper_offset_w,setup.paper_offset_h,setup.paper_width,setup.paper_height,name="Paper",color="green",fill="None",text=text)
        self.label_rect(fig,setup.drawing_offset_w,setup.drawing_offset_h,setup.drawing_width,setup.drawing_height,name="Drawing",color="blue",fill="None",text=text)
        for m in setup.magnets:
            self.magnet(fig,m)
        #self.magnet(fig,180,100,4)
        #self.magnet(fig,setup.bot_width - 180,100,4)

    def label_rect(self,fig,x,y,w,h,color="black",fill="none",name="",inside=False,text=True):
        top_offset = -3
        bottom_offset = 13
        if inside:
            top_offset = 13
            bottom_offset = -3
        self.rect(fig,x,y,w,h,width=1,color=color,fill=fill),
        if text:
            fig.append([
                sg.TextElement(x,y+top_offset, f"{name}: (x:{x},y:{y},w:{w},h:{h})", size=12, weight="bold"),
                sg.TextElement(x+w,y+h+bottom_offset, f"({x+w},y:{y+h})", size=12, weight="bold",anchor="end"),
            ] )
    
    def magnet(self,fig,mag,size=4):
        self.rect(fig,mag.x-size/2,mag.y-size/2,size,size,
                  color="red" if mag.active else "grey",
                  fill= "solid" if mag.active else "none")


    def rect(self,fig,x,y,w,h,width=1,color="black",fill="none"):
        points =[[x,y],[x+w,y],[x+w,y+h],[x,y+h],[x,y]]
        rect= sg.LineElement(points,width,color)
        rect.root.attrib['fill'] = fill
        fig.append([rect])
        #return rect
    
    def get_name(self):
        return "UNKNOWN"
    
    def run_test(self,setup,infile,process_dir="data/processed",check_dir="data/check",
                 output_dir="data/output", 
                 regen_dir="data/regen", regen_annot_dir="data/regen_annot",
                 do_transform=True, do_gcode=True, do_check=True):
        if not infile is pathlib.Path:
            infile = pathlib.Path(infile)
        stem = infile.stem
        processed = f"{process_dir}/{stem}_processed-{self.get_name()}.svg"
        check_svg = f"{check_dir}/{stem}_check-{self.get_name()}.svg"
        gcode = f"{output_dir}/{stem}-{self.get_name()}.gcode"
        check_gcode = f"{regen_dir}/{stem}-{self.get_name()}.svg"
        annot_check_gcode = f"{regen_annot_dir}/{stem}-{self.get_name()}.svg"
        print(f"\n*********************\n{self.get_name()} processing {infile} to {processed} and {gcode}\n***************")
        self.pipeline(setup,infile,processed,gcode,check_svg,check_gcode,annot_check_gcode,
                     do_transform=do_transform,do_gcode=do_gcode,do_check=do_check)
