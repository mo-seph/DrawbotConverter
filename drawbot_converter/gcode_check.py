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
    rect = sg.LineElement(points,"1.0","red")
    rect.root.attrib['fill'] = 'none'
    fig.append(rect)

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
                        sg.LineElement([[x1,y1],[x,y]],"1.0","black")
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
