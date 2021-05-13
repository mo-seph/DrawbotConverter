from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces
from svg_to_gcode.formulas import linear_map
from svg_to_gcode.geometry import Vector

class DrawbotInterface(interfaces.Gcode):
    def __init__(self):
        super().__init__()
        self._next_speed = 1
        self._current_speed = 1


    def set_movement_speed(self, speed) -> str:
        return ""

    def linear_move(self, x=None, y=None, z=None) -> str:
        if self.position is not None or (x is not None and y is not None):
            if x is None:
                x = self.position.x

            if y is None:
                y = self.position.y

            self.position = Vector(x, y)
        return f"g{x:.1f},{y:.1f}"

    # Override the laser_off method
    def laser_off(self):
        return "d0"

    # Override the set_laser_power method
    def set_laser_power(self, power):
        if power > 0:
            return "d1"
        else:
            return "d0"

    # We only do absolute!
    def set_absolute_coordinates(self) -> str:
        return ""

    def set_relative_coordinates(self) -> str:
        print("Aaargh! Can't do relative")
        return ""

    #def dwell(self, milliseconds) -> str:


def to_gcode(svgfile,gcodefile):
    gcode_compiler = Compiler(DrawbotInterface, movement_speed=1000, cutting_speed=300, pass_depth=0)
    curves = parse_file(svgfile) # Parse an svg file into geometric curves
    gcode_compiler.append_curves(curves)
    gcode_compiler.compile_to_file(gcodefile, passes=1)




if __name__ == '__main__':
    print("Converting SVG...")
    #to_gcode("output/scrambler_transformed.svg","output/scrambler_transformed.gcode")
    to_gcode("intermediate/circ5.svg","output/circ5.gcode")
