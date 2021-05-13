# Drawbot Server

This is a web server, possible with a python library, that will make it easy
to put SVG files onto the Drawbot. It:
- reads and maniupulates SVG files to put them into the right place on the page
- converts them into GCode for the polar plotter

## Strategies and Libraries

Currently using [SVGUtils](https://svgutils.readthedocs.io/) to read in and move
svg files around, and looking at [SvgToGcode](https://github.com/PadLex/SvgToGcode)
to do the conversion from SVG to GCode.

## Checking output

- Create SVG files that show bounding boxes
- Figure out a GCode viewer (or render it to an SVG?)

## Webserver

Todo, probably Flask?


# Other related stuff
- SVG Path Tools looks very powerful, might replace some of the work other libs are doing https://pypi.org/project/svgpathtools/
- svgo (javascript) looks like it does great SVG manip: https://github.com/svg/svgo
-
