import svgutils.transform as sg
import re

pen_down = re.compile("d1.*",re.IGNORECASE)
pen_up = re.compile("d0.*",re.IGNORECASE)
move = re.compile("g([\\d\\.-]+)\\s*,\\s*([\\d\\.-]+).*",re.IGNORECASE)


def gcode_to_svg(infile,outfile,width=760,height=580):
    w = f"{width}"
    h = f"{height}"
    drawing = False
    x1 = None
    y1 = None

    fig = sg.SVGFigure(width=w,height=h)
    fig.root.set('height',h)
    fig.root.set('width',w)

    points =[[0,0],[width,0],[width,height],[0,height],[0,0]]
    rect = sg.LineElement(points,"1.0","grey")
    rect.root.attrib['fill'] = 'none'
    fig.append(rect)
    top_limit = 170
    side_limit = 185
    # Draw a lightly filled bounding box

    r2 = sg.LineElement([
        [0,0],[width,0],[width,height],[width-side_limit,height],[width-side_limit,top_limit],[side_limit,top_limit],[side_limit,height],[0,height],[0,0]],"0.3","red")
    r2.root.attrib['fill'] = '#ff000010'
    fig.append(r2)
    with open(infile) as fp:
        for cnt, line in enumerate(fp):
            if pen_down.match(line):
                drawing=True
            elif pen_up.match(line):
                drawing=False
            elif move.match(line):
                m = move.match(line)
                x = float(m.group(1))
                y = float(m.group(2))
                if drawing:
                    fig.append(
                        sg.LineElement([[x1,y1],[x,y]],"0.2","black")
                    )
                else:
                    pass
                    #print(f"Moving from {x1},{y1} to {x},{y}")
                x1 = x
                y1 = y
            else:
                print(f"Unknown line: {line}")

    fig.save(outfile)




if __name__ == '__main__':
    gcode_to_svg("output/circ5.gcode","check/circ5_regen.svg")
