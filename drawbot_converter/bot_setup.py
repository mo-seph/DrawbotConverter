from dataclasses import dataclass

@dataclass
class BoundingBox:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    def width(self):
        return abs(self.xmax - self.xmin)
    def height(self):
        return abs(self.ymax - self.ymin)

    def translate_to(self,target):
        scale = target.width() / self.width()
        x_offset = target.xmin - self.xmin
        y_offset = target.ymin - self.ymin
        return Transform(scale, x_offset, y_offset)

    def place_inside(self,target):
        '''A bounding box that fits within the target, preseving scale'''
        width_scale = target.width() / self.width()
        height_scale = target.height() / self.height()

        scale = min(width_scale,height_scale)
        final_width = self.width() * scale
        final_height = self.height() * scale
        place_x = target.xmin + (target.width() - final_width )/2
        place_y = target.ymin + (target.height() - final_height )/2

        return BoundingBox(place_x,place_y,place_x + final_width,place_y + final_height)

    def __str__(self):
        return f"BoundingBox: [{self.xmin},{self.ymin}] to [{self.xmax},{self.ymax}]"

@dataclass
class Transform:
    scale: float
    x_offset: float
    y_offset: float

    def __str__(self):
        return f"Transform: [scale:{self.scale},x:{self.x_offset},y:{self.y_offset}]"

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

    def top_center_drawing(self,offset):
        self.drawing_offset_w = self.paper_offset_w + (self.paper_width - self.drawing_width)/2
        self.drawing_offset_h = self.paper_offset_h + offset
        return self

    def bot_box(self):
        '''Returns BoundingBox of the Bot'''
        return BoundingBox( 0, 0, self.bot_width, self.bot_height)


    def paper_box(self):
        '''Returns BoundingBox of the paper on the bot'''
        return BoundingBox(
            self.paper_offset_w,
            self.paper_offset_h,
            self.paper_offset_w + self.paper_width,
            self.paper_offset_h+ self.paper_height)

    def drawing_box(self):
        '''Returns BoundingBox for the drawing to fit in'''
        return BoundingBox(
            self.drawing_offset_w,
            self.drawing_offset_h,
            self.drawing_offset_w + self.drawing_width,
            self.drawing_offset_h+ self.drawing_height)

    def place_image(self,image_box:BoundingBox) -> BoundingBox :
        return image_box.place_inside(self.drawing_box())
