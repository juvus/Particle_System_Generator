# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFilter, ImageFont

class SinglePicture():
    def __init__(self):
        self.scale = None  # Scale of the picture [um/pix]
        self.realWidth = None  # Real width of the particle [um]
        self.margins = None  # Flag to use margins or not [boolean]
        self.marginWidth = None  # Width of the margins [pix]
        self.coordinates = None  # Coordinates of the particle points (in 360x360 picture)
        self.picWidthHeight = None  # Desired width and height of the picture
        self.picParticleColor = None  # Particle color
        self.picBkgColor = None  # Background color
        self.picShowScale = None  # Flag to show or not the scale on picture
        self.picture = None  # Picture of the singe particle 
        self.blurPict = None  # Blured (filtered) picture of the single particle
        self.blurRadius = 0.5  # Blur of the final render
    
    def get_single_picture(self, realWidth, margins, coordinates, picWidthHeight,
                           picParticleColor, picBkgColor, picShowScale):
        """Method for generating the single picture of the particle (*.png format)
        Args:
            realWidth [float]: Real width of the particle [um] (for scale drawing)
            margins [bln]: Bolean flag to whether add margins or not
            coordinates [[x,y],...]: coordinates of the particle points (in 360x360 picture)
            picWidthHeight [px]: Desired width and height of the picture
            picParticleColor [r,g,b]: Particle color
            picBkgColor [r,g,b]: Background color
            picShowScale [bln]: Flag to show or not the scale on picture
        """
        # Save the picture parameters
        self.realWidth = realWidth
        self.margins = margins
        self.coordinates = coordinates
        self.picWidthHeight = picWidthHeight
        self.picParticleColor = picParticleColor
        self.picBkgColor = picBkgColor
        self.picShowScale = picShowScale
        
        # Calculate margin width (5% from the picture width)
        self.marginWidth = int(round(self.picWidthHeight * 0.05))
        
        # Resize the picture from 360 pix to desired width
        k = (self.picWidthHeight - self.marginWidth * 2) / 360  # Proportional coefficient
        timeArray = []
        for point in self.coordinates:
            lst = list(point)
            lst[0] = int(round(lst[0] * k))
            lst[1] = int(round(lst[1] * k))
            timeArray.append(tuple(lst))
        self.coordinates = tuple(timeArray)
        
        #  Recalculate the particle vertices coordinates using margins            
        if self.margins:
            timeArray = []
            for point in self.coordinates:
                lst = list(point)
                lst[0] += self.marginWidth
                lst[1] += self.marginWidth
                timeArray.append(tuple(lst))
            self.coordinates = tuple(timeArray) 
        else:
            self.marginWidth = 0
        
        # Recalculate new picture scale
        self.scale = self.realWidth / (self.picWidthHeight - self.marginWidth * 2)
        
        # Create a picture with background and particle
        r = self.picBkgColor[0]
        g = self.picBkgColor[1]
        b = self.picBkgColor[2]
        self.picture = Image.new('RGB', (self.picWidthHeight, self.picWidthHeight), (r, g, b))
        
        # Draw the particle in the created picture
        r = self.picParticleColor[0]
        g = self.picParticleColor[1]
        b = self.picParticleColor[2]
        self.draw = ImageDraw.Draw(self.picture) 
        self.draw.polygon(self.coordinates, fill=(r, g, b), outline=(r, g, b))
        
        # Add blur
        self.blurPict = self.picture.filter(ImageFilter.GaussianBlur(radius=self.blurRadius))
        
        # Drawing the scale in the bottom
        if self.picShowScale:
            self.draw = ImageDraw.Draw(self.blurPict)
            x0 = self.marginWidth  # Start point of the scale (X)
            y0 = self.picWidthHeight - self.marginWidth  # Start point of the scale (Y)
            h = int(round(self.picWidthHeight * 3 / 400))  # Width of the scale   
            part = (self.picWidthHeight - self.marginWidth * 2) / 5
            self.draw.rectangle((x0 + part*0, y0, x0 + part*1, y0 + h), fill='red', outline='white')
            self.draw.rectangle((x0 + part*1, y0, x0 + part*2, y0 + h), fill='white', outline='white')
            self.draw.rectangle((x0 + part*2, y0, x0 + part*3, y0 + h), fill='red', outline='white')
            self.draw.rectangle((x0 + part*3, y0, x0 + part*4, y0 + h), fill='white', outline='white')
            self.draw.rectangle((x0 + part*4, y0, x0 + part*5, y0 + h), fill='red', outline='white')
            
            # Define font size, type and its position
            fontWidth = int(round(self.picWidthHeight * 11 / 400))
            x = int(round(self.picWidthHeight / 3.3))  # X Position of the text
            y = int(round(y0 + self.picWidthHeight * 5 / 400))  # Y position of the text      
            font = ImageFont.truetype('./Resources/arial.ttf', fontWidth, encoding="utf-8")
            self.draw.text((x, y), '{0:.1f} [\u03BCm]; Scale: {1:.3f} [\u03BCm/pix]'.format(self.realWidth, self.scale), font=font)

    def save_picture(self, path):
        '''Method for saving the picture
        Args:
            path [str]: path of the file to be saved'''
        self.blurPict.save(path)
        
    def show_picture(self):
        '''Method to show the particle picture in the default editor'''
        self.blurPict.show()
    
        
        
    

