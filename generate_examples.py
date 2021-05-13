import svgutils.transform as sg
from lxml import etree


# Simple square in native size
width="10mm"
height="10mm"
fig = sg.SVGFigure(width=width,height=height)
fig.root.set('height',height)
fig.root.set('width',width)
points =[[0,0],[10,0],[10,10],[0,10],[0,0]]
rect= sg.LineElement(points,1,"black")
rect.root.attrib['fill'] = "None"
fig.append([rect])
fig.save("test/simple_square_initial.svg")


# Simple square but ready to go on a page
width="700mm"
height="700mm"
fig = sg.SVGFigure(width=width,height=height)
fig.root.set('height',height)
fig.root.set('width',width)

points =[[200,200],[500,200],[500,500],[200,500],[200,200]]
rect= sg.LineElement(points,1,"black")
rect.root.attrib['fill'] = "None"
fig.append([rect])
fig.save("test/simple_square_transformed.svg")
