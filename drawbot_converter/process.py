import drawbot_converter.svg_transform as svgt
import drawbot_converter.svgcode as sgc
import drawbot_converter.gcode_check as gcc

import pathlib

def process(setup:svgt.BotSetup, file, intermediate, check_svg,gcode, check_gcode) :
        svgt.transform(setup,file,intermediate,check_svg)
        sgc.to_gcode(intermediate,gcode)
        gcc.gcode_to_svg(gcode,check_gcode,width=setup.bot_width,height=setup.bot_height)



if __name__ == '__main__':

    #file = "input/circle_5_positive_ripple_minified.svg"
    #file = "input/hexshell.svg"
    file = "input/hexshell_minified.svg"

    s = svgt.BotSetup(
        bot_width=760,
        bot_height=580,
        paper_width=584,
        paper_height=420,
        drawing_width=200,
        drawing_height=200
    ).center_paper().center_drawing()

    path = pathlib.PurePath(file)
    stem = path.stem
    intermediate = f"intermediate/{stem}_processed.svg"
    check_svg = f"check/{stem}_check.svg"
    gcode = f"output/{stem}.gcode"
    check_gcode = f"check/{stem}_regen.svg"
