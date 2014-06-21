from zoundry.base.util.text.textutil import getNoneString
import re

class ZCssColor:
    u"""Wraps CSS color information""" #$NON-NLS-1$
    
    # The basic (original) 16 color names defined by the W3C.
    COLOR_NAMES = {
            u"aqua" : u"#00FFFF", u"navy"   : u"#000080", u"black"   : u"#000000", u"olive"  : u"#808000", #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$ #$NON-NLS-8$
            u"blue" : u"#0000FF", u"purple" : u"#800080", u"fuchsia" : u"#FF00FF", u"red"    : u"#FF0000", #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$ #$NON-NLS-8$
            u"gray" : u"#808080", u"silver" : u"#C0C0C0", u"green"   : u"#008000", u"teal"   : u"#008080", #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$ #$NON-NLS-8$
            u"lime" : u"#00FF00", u"white"  : u"#FFFFFF", u"maroon"  : u"#800000", u"yellow" : u"#FFFF00"  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$ #$NON-NLS-8$
    }
    
    RGB_INT_RE_PATTERN = re.compile(u"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)",re.IGNORECASE) #$NON-NLS-1$
    RGB_PERCENT_RE_PATTERN = re.compile(u"rgb\s*\(\s*(\d+%)\s*,\s*(\d+%)\s*,\s*(\d+%)\s*\)",re.IGNORECASE); #$NON-NLS-1$
    
    def __init__(self, cssValue = None, red = 0, blue = 0, green = 0):      
        self.red = 0
        self.blue = 0
        self.green = 0
        self.cssValue = u"#000000" #$NON-NLS-1$
        self.valid = True
        if red:
            self.red = self._limitValue(red)
        if green:
            self.green = self._limitValue(green)
        if blue:
            self.blue = self._limitValue(blue)
        if getNoneString(cssValue):
            self.setCssColor(cssValue)
        
    def _limitValue(self, v):
        if v and v > 255:
            return 255
        elif v and v < 0:
            return 0
        else:
            return v
            
    def _intToPercent(self, aIntVal):
        aIntVal = self._limitValue(aIntVal)
        if aIntVal >= 0 and aIntVal <= 255:
            return int(aIntVal / 255.0 * 100.0)
        elif aIntVal > 255:
            return 100
        else:
            return 0

    def _percentToInt(self,aPercent):
        if aPercent and aPercent >= 0 and aPercent <= 255:
            return int(aPercent/100.0 * 255)
        return 255
        
    def _intToHex(self,  aIntVal):
        s = hex(aIntVal)
        s = s[2:]
        if (len(s) == 1):
            s = u"0" + s #$NON-NLS-1$
        return s
      
    def isValid(self):
        u"""Returns true if the color was correctly parsed""" #$NON-NLS-1$
        return self.valid
        
    def getRed(self):
        u"""Returns value of red (0-255)""" #$NON-NLS-1$
        return self.red
        
    def getGreen(self):
        u"""Returns value of green (0-255)""" #$NON-NLS-1$
        return self.green
        
    def getBlue(self):
        u"""Returns value of blue (0-255)""" #$NON-NLS-1$
        return self.blue
        
    def getRGB(self):
        u"""Returns rgb value in decimal rgb(r,g,b)""" #$NON-NLS-1$
        params = ( str(self.red), str(self.green), str(self.blue) )
        return u"rgb(%s,%s,%s)" % params #$NON-NLS-1$

    def getRGBPercent(self):
        u"""Returns rgb value in percentage rgb(r%, g%, b%)""" #$NON-NLS-1$
        params = (
            str(self._intToPercent(self.red)), str(self._intToPercent(self.green)),
            str(self._intToPercent(self.blue))
        )
        return u"rgb(%s%%,%s%%,%s%%)" % params #$NON-NLS-1$

    def getCssColor(self):
        u"""Returns CSS hex value as #rrggbb in hex""" #$NON-NLS-1$
        return u"#" + str(self._intToHex(self.red)) + str(self._intToHex(self.green))  + str(self._intToHex(self.blue)) #$NON-NLS-1$
        
    def setCssColor(self, aCssColor):
        u"""Parses the CSS color string and returns true if successful.""" #$NON-NLS-1$
        self.valid = False
        if not aCssColor or not aCssColor.strip():
            return False            
        aCssColor = aCssColor.strip().lower()
        
        if ZCssColor.COLOR_NAMES.has_key(aCssColor):
            aCssColor = ZCssColor.COLOR_NAMES[aCssColor]
        l = len(aCssColor)
        
        if aCssColor[0] == u'#' and l == 4: #$NON-NLS-1$
            # #rgb
            self.red = int(aCssColor[1] + aCssColor[1], 16)
            self.green = int(aCssColor[2] + aCssColor[2], 16)
            self.blue = int(aCssColor[3] + aCssColor[3], 16)
            self.valid = True
            return True
        elif aCssColor[0] == u'#' and l == 7: #$NON-NLS-1$
            # #rrggbb
            self.red = int(aCssColor[1:3], 16)
            self.green = int(aCssColor[3:5], 16)
            self.blue = int(aCssColor[5:], 16)
            self.valid = True
            return True
    
        m = re.match(ZCssColor.RGB_INT_RE_PATTERN, aCssColor)
        if m:
            self.red = self._limitValue( int(m.group(1)) )
            self.green = self._limitValue( int(m.group(2)) )
            self.blue = self._limitValue( int(m.group(3)) )
            self.valid = True
            return True
        m = re.match(ZCssColor.RGB_PERCENT_RE_PATTERN, aCssColor)
        if m:
            self.red = self._limitValue( self._percentToInt( int(m.group(1)[:-1]) ) )
            self.green = self._limitValue( self._percentToInt( int(m.group(2)[:-1]) ) )
            self.blue = self._limitValue( self._percentToInt( int(m.group(3)[:-1])) )
            self.valid = True
            return True
        return False

#end ZCssColor class 
