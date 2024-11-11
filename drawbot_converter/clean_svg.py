
from svgpathtools import svg2paths2, wsvg

def clean(infile,outfile,method="python"):
    if method == "python":
        clean_python(infile,outfile)

def clean_python(infile,outfile):
    paths, attributes,svg_attributes = svg2paths2(infile)
    print(f"Attributes: {attributes}\n\nSVG Atts: {svg_attributes}\n\n")
    wsvg(paths, attributes=attributes, svg_attributes=svg_attributes, filename=outfile)

def clean_javascript(infile,outfile):
    pass



if __name__ == "__main__":
    basedir="/Users/dmurrayrust/Dropbox/Projects/CNCExplorations/ca/output"
    filename="circle_5_positive_ripple.svg"
    clean_python(f"{basedir}/{filename}",f"intermediate/{filename}")
