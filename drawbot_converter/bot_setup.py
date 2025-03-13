from dataclasses import dataclass,field

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

    def fill_target(self, target):
        '''A bounding box that fills the target, preserving scale but potentially extending beyond target bounds'''
        width_scale = target.width() / self.width()
        height_scale = target.height() / self.height()

        scale = max(width_scale, height_scale)  # Use max instead of min to fill rather than fit
        final_width = self.width() * scale
        final_height = self.height() * scale
        place_x = target.xmin + (target.width() - final_width) / 2
        place_y = target.ymin + (target.height() - final_height) / 2

        return BoundingBox(place_x, place_y, place_x + final_width, place_y + final_height)
    def __str__(self):
        return f"BoundingBox => min:[{self.xmin},{self.ymin}] max: [{self.xmax},{self.ymax}]"

@dataclass
class Transform:
    scale: float
    x_offset: float
    y_offset: float

    def __str__(self):
        return f"Transform: [scale:{self.scale},x:{self.x_offset},y:{self.y_offset}]"

@dataclass
class Magnet:
    x: float
    y: float
    active: bool = True

@dataclass
class BotSetup:
    bot_width:float = 760
    bot_height:float = 680
    paper_width:float = 418
    paper_height:float = 297 # *2 for A2
    drawing_width:float = 380
    drawing_height:float = 150
    paper_offset_w:float = 0
    paper_offset_h:float = 0
    drawing_offset_w:float = 0
    drawing_offset_h:float = 0
    fill_target: bool = False
    magnets: list[Magnet] = field(default_factory=list)
    minimum_y_offset:float = 175
    x_margins:float = 185

    def center_paper(self):
        self.paper_offset_w = (self.bot_width - self.paper_width)/2
        self.paper_offset_h = (self.bot_height - self.paper_height)/2
        return self

    def top_center_paper(self,offset):
        self.paper_offset_w = (self.bot_width - self.paper_width)/2
        self.paper_offset_h = offset
        return self

    def center_drawing(self):
        self.drawing_offset_w = self.paper_offset_w + (self.paper_width - self.drawing_width)/2
        self.drawing_offset_h = self.paper_offset_h + (self.paper_height - self.drawing_height)/2
        return self

    def top_center_drawing(self,offset):
        self.drawing_offset_w = self.paper_offset_w + (self.paper_width - self.drawing_width)/2
        self.drawing_offset_h = self.paper_offset_h + offset
        return self

    def add_magnets(self,inset,height,active=True):
        self.magnets.append(Magnet(inset,height,active))
        self.magnets.append(Magnet(self.bot_width-inset,height,active))
        return self
    
    def a3_paper(self,paper_offset_h=80,drawing_offset_h=80):
        self.paper_width = 420
        self.paper_height = 297
        self.paper_offset_h = paper_offset_h
        self.drawing_offset_h = drawing_offset_h
        return self
    
    def a2_paper(self,paper_offset_h=80,drawing_offset_h=80 ):
        self.paper_width = 420
        self.paper_height = 594
        self.paper_offset_h = paper_offset_h
        self.drawing_offset_h = drawing_offset_h
        return self
    
    def rodalm_13_18(self):
        self.drawing_width = 150
        self.drawing_height = 100
        return self
    
    def rodalm_13_18_raw(self):
        self.drawing_width = 180
        self.drawing_height = 130
        return self
    
    def rodalm_21_30(self):
        self.drawing_width = 180
        self.drawing_height = 130
        return self
    
    def rodalm_30_40(self):
        self.drawing_width = 210
        self.drawing_height = 300
        return self
    
    def rodalm_40_50(self):
        self.drawing_width = 300
        self.drawing_height = 400
        return self

    def sannahed_25(self):
        self.drawing_width = 130
        self.drawing_height = 130
        return self
    
    def sannahed_25_raw(self):
        self.drawing_width = 250
        self.drawing_height = 250
        return self
    
    
    def standard_magnets(self):
        self.add_magnets(inset=180,height=100) \
            .add_magnets(inset=105,height=175,active=False) \
            .add_magnets(inset=180,height=250,active=True)
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
        if self.fill_target:
            return image_box.fill_target(self.drawing_box())
        return image_box.place_inside(self.drawing_box())

    @classmethod
    def from_json(cls, json_data: dict, transforms: list[str] = None):
        """Create a BotSetup instance from a JSON object and apply optional transforms.
        
        Example JSON:
        {
            "bot_width": 760,
            "bot_height": 580,
            "transforms": ["a3_paper", "center_paper", ["add_magnets", 180, 100]]
        }
        """
        # Extract transforms from JSON if not provided as argument
        transforms = transforms or json_data.get('transforms', [])
        
        # Remove transforms from json_data to avoid passing it to constructor
        if 'transforms' in json_data:
            json_data = {k: v for k, v in json_data.items() if k != 'transforms'}
        
        # Create instance with basic properties
        instance = cls(**json_data)
        
        # Apply transforms
        for transform in transforms:
            if isinstance(transform, list):
                # Handle transforms with arguments: ["method_name", arg1, arg2, ...]
                method_name, *args = transform
                method = getattr(instance, method_name)
                method(*args)
            else:
                # Handle simple transforms: "method_name"
                method = getattr(instance, transform)
                method()
        
        return instance
