# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageEnhance
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QPixmap, QImage
import math as m

class RealImage():
    def __init__(self, N):
        self.N = N  # Number of polygon vertices
        self.path = ''  # Path to the image
        self.image = Image.new('RGBA', (360, 360), (255, 255, 255, 255)) # Default image  
        self.imageMod = self.image.copy()
        self.origImage = self.image.copy()  # Original image without any modifications
        self.angle = 0  # Current angle of the picture     
        self.offsetX = 0  # Offset along X axis
        self.offsetY = 0  # Offset along Y axis
        self.offsetRightLimit = 0  # Limit to shift to the right side
        self.offsetLeftLimit = 0  # Limit to shift to the left side
        self.offsetUpLimit = 0  # Limit to shift to the up side
        self.offsetDownLimit = 0  # Limit to shift to the down side          
        self.ratio = 1  # Current magnification of the image
        self.ratioInit = 1  # Initial ratio of the image
        #self.calc_shift_limits()
        self.ratioMin = 0.02  # Minimum posible ratio
        self.ratioMax = 2  # Maximum posible ratio
        self.color = 1.0  # Current color (saturation) of the image
        self.brightness = 1.0  # Current brightness of the image
        self.contrast = 1.0  # Current contrast of the image
        self.sharpness = 1.0  # Current sharpness of the image
        self.transp = 1.0  # Current transparency (0 - white, 1 - original)
        self.generate_mask()  # Generate mask for image cutting to polygon
        self.calc_shift_limits()
        
    def put_in_middle(self, width, height):
        """Method for putting in the moddle of 360x360 picture our image"""
        background = Image.new('RGBA', (360, 360), (255, 255, 255, 255))  # White background image
        offsetX = 180 - int(round(width / 2))
        offsetY = 180 - int(round(height / 2))
        background.paste(self.imageMod, (offsetX, offsetY))
        self.imageMod = background.copy()
        
    def set_N(self, N):
        self.N = N
        self.generate_mask()   
    
    def generate_mask(self):
        """Method for generation the transparancy mask"""
        # Generate coordinates
        array = []
        for i in range(self.N):
            angle = i * 2 * m.pi/self.N
            x = int(round(180 + 180 * m.cos(angle)))
            y = int(round(180 + 180 * m.sin(angle)))
            array.append((x, y))
        # Generate the mask of polygon shape
        self.mask = Image.new('1', (360, 360), 'black')  # Black square
        draw = ImageDraw.Draw(self.mask)
        draw.polygon(array, fill='white')
    
    def open_image(self, path):
        """Method to open the image file"""
        # Some tricks to avoid transparency of the image (and open RGB files as well)
        self.image = Image.open(path).convert('RGBA')
        background = Image.new('RGBA', self.image.size, (255, 255, 255))
        self.image = Image.alpha_composite(background, self.image)
        self.imageMod = self.image.copy()
        self.origImage = self.image.copy()  # Store the original image
   
        width = self.image.size[0]
        height = self.image.size[1]
        
        # Adapt the image to the 360x360 size (with adding fields) + determine ratio
        if width > height:
            if width >= 360:  # Image is needed to be resized
                self.ratio = width / 360  
                newHeight = int(round(height / self.ratio))
                self.imageMod = self.imageMod.resize((360, newHeight), Image.ANTIALIAS)
                self.put_in_middle(360, newHeight)
            else:  # No resize to image nedeed, put image in the center
                self.ratio = 1.0
                self.put_in_middle(width, height)
        elif height > width:
            if height >= 360:  # Image is needed to be resized
                self.ratio = height / 360
                newWidth = int(round(width / self.ratio))
                self.imageMod = self.imageMod.resize((newWidth, 360), Image.ANTIALIAS)
                self.put_in_middle(newWidth, 360) 
            else:  # No resize to image nedeed, put image in the center
                self.ratio = 1.0
                self.put_in_middle(width, height)      
        elif width == height:
            if width >= 360:  # Image is needed to be resized
                self.ratio = width / 360
                self.imageMod = self.imageMod.resize((360, 360), Image.ANTIALIAS)
            else: # No resize to image needed, put image in the center
                self.ratio = 1.0
                self.put_in_middle(width, height)
        self.ratioInit = self.ratio
        self.ratioMax = self.ratio * 2  # Maximum possible ratio
        self.calc_shift_limits()
        # Set defaults numbers
        self.angle = 0
        self.offsetX = 0
        self.offsetY = 0   
        self.transform(self.angle, (self.offsetX, self.offsetY))
        
    def save_image(self, path):
        self.imageMod.save(path)   
    
    def calc_shift_limits(self):
        self.offsetRightLimit = 180 * self.ratio + self.image.size[0]/2
        self.offsetLeftLimit = -self.offsetRightLimit
        self.offsetDownLimit = 180 * self.ratio + self.image.size[1]/2
        self.offsetUpLimit = -self.offsetDownLimit
               
    def convert_to_QPixmap(self):
        qim = ImageQt(self.imageMod)
        pix = QPixmap.fromImage(qim)
        return pix
 
    def transform(self, angle, offset):
        self.angle = angle  # Update the current angle of the image

        self.offsetX = int(round(offset[0])) #left/right (i.e. 5/-5)
        self.offsetY = int(round(offset[1])) #up/down (i.e. 5/-5)      
        
        # 1. Crop the image
        x1 = self.image.size[0]/2 - 180 * self.ratio # X of top left
        y1 = self.image.size[1]/2 - 180 * self.ratio # Y of top left
        x2 = self.image.size[0]/2 + 180 * self.ratio # X of bottom right
        y2 = self.image.size[1]/2 + 180 * self.ratio # Y of bottom right
         
        area = (x1 - self.offsetX, y1 - self.offsetY, x2 - self.offsetX, y2 - self.offsetY)
        self.imageMod = self.image.crop(area)
        
        # 2. Apply scaling to the croped image
        self.imageMod = self.imageMod.resize((360, 360), Image.ANTIALIAS)
         
        # 3. Add the white margins to all the sides from the image
        background = Image.new('RGBA', (360, 360), (255, 255, 255, 255))  # White background image
        background.paste(self.imageMod, (0, 0), self.imageMod)
        self.imageMod = background.copy()
        
        # 4. Rotate the image
        self.imageMod = self.imageMod.rotate(-angle, center=(self.imageMod.size[0]/2, self.imageMod.size[1]/2))
        
        # 5. Apply the transparency mask to the final image (cut to be a polygon)
        background = Image.new('RGBA', (360, 360), (0, 0, 0, 0))  # Transparent background
        background.paste(self.imageMod, (0, 0), self.mask)
        self.imageMod = background.copy()
        
    def set_enhance(self, color, brightness, contrast, sharpness, transp):
        """Method to enhance the image"""
        self.color = color
        self.brightness = brightness
        self.contrast = contrast
        self.sharpness = sharpness
        self.transp = transp

        # Enhance color
        enhancer = ImageEnhance.Color(self.origImage)
        self.image = enhancer.enhance(self.color)

        # Enhance brightness (from 0 (0) - 1 (5), 0.5 is original image)
        enhancer = ImageEnhance.Brightness(self.image)
        if self.brightness <= 0.5:
            self.image = enhancer.enhance(2 * self.brightness + 0)
        else:
            self.image = enhancer.enhance(8 * self.brightness - 3)

        # Enhance contrast (from 0 (0) - 1 (5), 0.5 is original image)
        enhancer = ImageEnhance.Contrast(self.image)
        if self.contrast <= 0.5:
            self.image = enhancer.enhance(2 * self.contrast + 0)
        else:
            self.image = enhancer.enhance(8 * self.contrast - 3)
            
        # Enhance sharpness (from 0 (0) - 1 (3), 0.5 is original image)
        enhancer = ImageEnhance.Sharpness(self.image)
        if self.sharpness <= 0.5:
            self.image = enhancer.enhance(2 * self.sharpness + 0)
        else:
            self.image = enhancer.enhance(8 * self.sharpness - 3)
 
        # Apply thansparency to white (0 - white, 1 - original)
        background = Image.new('RGBA', self.image.size, (255, 255, 255, 255))
        value = int(round(self.transp * 255))
        mask = Image.new('L', self.image.size, value)
        background.paste(self.image, (0, 0), mask)
        self.image = background.copy()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
