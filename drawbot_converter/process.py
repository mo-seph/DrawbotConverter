#import drawbot_converter.svg_transform2 as svgt2
#import drawbot_converter.transformer_svgutils as svgt1
import drawbot_converter.svgcode as sgc
import drawbot_converter.gcode_check as gcc
import drawbot_converter.clean_svg as csvg
from drawbot_converter.bot_setup import BotSetup

from drawbot_converter.transformer_svgutils import TransformerSVGUtils
from drawbot_converter.transformer_svgpathtools import TransformerSVGPathTools

# import module
import traceback

# file=input SVG; processed=moved/scaled SVG; check_svg=processed with labels on; gcode=real gcode output; check_gcode=convert gcode to svg file
def process1(setup:BotSetup, file, processed, check_svg,gcode, check_gcode) :
    print(f"+++ Transform 1 on {file}")
    #csvg.clean(file,cleaned)
    svgt1.transform(setup,file,processed,check_svg)
    sgc.to_gcode(processed,gcode)
    gcc.gcode_to_svg(gcode,check_gcode,width=setup.bot_width,height=setup.bot_height)

def process2(setup:BotSetup, file, processed, check_svg,gcode, check_gcode) :
    print(f"+++ Transform 2 on {file}")
    #csvg.clean(file,cleaned)
    svgt2.transform(setup,file,processed,check_svg)
    sgc.to_gcode(processed,gcode)
    gcc.gcode_to_svg(gcode,check_gcode,width=setup.bot_width,height=setup.bot_height)



if __name__ == '__main__':
    import pathlib
    import os
    import sys


    #file = "input/circle_5_positive_ripple_minified.svg"
    #file = "input/hexshell.svg"
    #file = "input/hexshell_minified.svg"

    s = BotSetup(
        bot_width=760,
        bot_height=580,
        paper_width=418,
        paper_height=297, # *2 for A2
        drawing_width=380,
        #drawing_height=380
        drawing_height=150
    ).add_magnets(inset=180,height=100) \
        .top_center_paper(90).top_center_drawing(40)
        #.add_magnets(inset=140,height=160,active=False) \

    if len(sys.argv) > 1:
        pathlist = [pathlib.Path(sys.argv[1])]
    else:
        pathlist = pathlib.Path("data/test").glob('**/*.svg')
    processors = [
        #TransformerSVGUtils(), 
        TransformerSVGPathTools()
    ]
    for path in pathlist:
        for p in processors:
            #path = pathlib.PurePath(file)
            #stem = path.stem
            #processed = f"data/processed/{stem}_processed-{i}.svg"
            #check_svg = f"data/check/{stem}_check-{i}.svg"
            #gcode = f"data/output/{stem}-{i}.gcode"
            #check_gcode = f"data/regen/{stem}-{i}.svg"
            #print(f"\n*********************\nProcessing {path} to {processed} and {gcode}\n***************")
            try:
                p.run_test(s,path,do_transform=True)
                #processors[i](s,str(path),processed,check_svg,gcode,check_gcode)
            except Exception as e:
                print(f"Couldn't process path {path}:\n{e}")
                traceback.print_exc()
