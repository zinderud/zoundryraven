from zoundry.base.util.text.textutil import getSafeString

#---------------------------------------
# HTML Table insert/edit mode
#---------------------------------------
class ZHtmlTableModel:

    def __init__(self, tableAttributes):
        self.insertMode = tableAttributes is None
        self.border = self._getAttrCssUnitValue(tableAttributes, u"border", None) #$NON-NLS-1$ 
        self.padding = self._getAttrCssUnitValue(tableAttributes, u"cellpadding", None) #$NON-NLS-1$ 
        self.spacing = self._getAttrCssUnitValue(tableAttributes, u"cellspacing", None) #$NON-NLS-1$
        self.rows = self._getAttrIntValue(tableAttributes, u"rows", 2) #$NON-NLS-1$
        self.cols = self._getAttrIntValue(tableAttributes, u"cols", 2) #$NON-NLS-1$
        if self.insertMode:
            self.width = u"350" #$NON-NLS-1$
        else:
            self.width = self._getAttrCssUnitValue(tableAttributes, u"width", None) #$NON-NLS-1$ 
    # end __init__()

    def _getAttrIntValue(self, attrsMap, attrName, defaultValue):
        if attrsMap is not None and attrsMap.has_key(attrName) and attrsMap[attrName]:
            return int(attrsMap[attrName])
        else:
            return defaultValue
    # end _getAttrIntValue()
    
    def _getAttrCssUnitValue(self, attrsMap, attrName, defaultValue):
        if attrsMap is not None and attrsMap.has_key(attrName):
            return getSafeString(attrsMap[attrName])
        else:
            return defaultValue
    # end _getAttrCssUnitValue()    

    def isInsertMode(self):
        return self.insertMode
    # end isEditMode()

    def getRows(self):
        return self.rows
    # end

    def setRows(self, rows):
        self.rows = rows
    # end

    def getCols(self):
        return self.cols
    # end

    def setCols(self, cols):
        self.cols = cols
    # enbd

    def getPadding(self):
        return self.padding
    # end

    def setPadding(self, padding):
        self.padding = padding
    # end

    def getSpacing(self):
        return self.spacing
    # end

    def setSpacing(self, spacing):
        self.spacing = spacing
    # end

    def getBorder(self):
        return self.border
    # end

    def setBorder(self, border):
        self.border = border
    # end

    def getWidth(self):
        return self.width
    # end

    def setWidth(self, width):
        self.width = width
    # end

    def getTableAttributes(self):
        attrs = {}
        attrs[u"rows"] = u"%d" % self.rows #$NON-NLS-1$ #$NON-NLS-2$
        attrs[u"cols"] = u"%d" % self.cols #$NON-NLS-1$ #$NON-NLS-2$
        if self.padding is not None:
            attrs[u"cellpadding"] = u"%s" % self.padding #$NON-NLS-1$ #$NON-NLS-2$
        if self.spacing is not None:
            attrs[u"cellspacing"] = u"%s" % self.spacing #$NON-NLS-1$ #$NON-NLS-2$
        if self.width is not None:
            attrs[u"width"] = u"%s" % self.width #$NON-NLS-1$ #$NON-NLS-2$
        if self.border is not None:
            attrs[u"border"] = u"%s" % self.border #$NON-NLS-1$ #$NON-NLS-2$
        return attrs
    # end getTableAttributes()

# end ZHtmlTableModel

