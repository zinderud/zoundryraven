from zoundry.base.util.text.textutil import getNoneString
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlelements import getDispElement
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import IZXHTMLEditControlTableContext


# ------------------------------------------------------------------------------
# Contains table instance inforamtion
# ------------------------------------------------------------------------------
class ZMshtmlTableContext:
    ABOVE = 0
    BELOW = 1
    LEFT = 0
    RIGHT = 1

    def __init__(self, tableDispEle, rowDispEle, cellDispEle, parentTableInfo):
        self.tableDispEle = tableDispEle
        self.rowDispEle = rowDispEle
        self.cellDispEle = cellDispEle
        self.parentTableInfo = parentTableInfo
    # end __init__()

    def getParent(self):
        return self.parentTableInfo
    # end getParent()

    def canInsertRow(self, where): #@UnusedVariable
        return self.rowDispEle is not None and self.rowDispEle.parentElement.tagName == u"TBODY" #$NON-NLS-1$
    # canInsertRow()

    def insertRow(self, where): #@UnusedVariable
        if self.rowDispEle is None:
            return
        # insert row from current tBody
        i = -1
        tbodyDisp = getDispElement(self.rowDispEle.parentElement)
        if ZMshtmlTableContext.ABOVE == where:
            i = self.rowDispEle.rowIndex - 1
            if i < 0:
                i = 0
        else:
            i = self.rowDispEle.rowIndex + 1
            if i >= tbodyDisp.rows.length:
                i = -1
        newRow = tbodyDisp.insertRow(i)
        numcols = self.rowDispEle.cells.length
        for i in range(numcols):
            newRow.insertCell(-1)
    # insertRow()

    def canInsertCol(self, where): #@UnusedVariable
        return self.cellDispEle is not None
    # canInsertCell()

    def insertCol(self, where): #@UnusedVariable
        if self.cellDispEle is None:
            return
        cellIndex = self.cellDispEle.cellIndex
        numrows = self.tableDispEle.rows.length
        numcols = self.rowDispEle.cells.length
        i = 0
        if ZMshtmlTableContext.LEFT == where:
            i = cellIndex
        else:
            i = cellIndex + 1
            if i >= numcols:
                i = -1
        for r in range(numrows):
            row = self.tableDispEle.rows[r]
            # FIXME (PJ) insert TH elem right after TH(i-1)
#            if row.parentElement.tagName == u"THEAD": #$NON-NLS-1$
#                th =
            cell = row.insertCell(i)
            cell.innerText = u"cell" #$NON-NLS-1$
    # insertCol()

    def canMoveRow(self, where):
        tbodyRows = 0
        if self.rowDispEle and self.rowDispEle.parentElement:
            tbodyDisp = getDispElement(self.rowDispEle.parentElement)
            tbodyRows = tbodyDisp.rows.length
        if self.rowDispEle and ZMshtmlTableContext.ABOVE == where and self.rowDispEle.sectionRowIndex > 0:
            return True
        elif self.rowDispEle and ZMshtmlTableContext.BELOW == where and self.rowDispEle.sectionRowIndex < (tbodyRows - 1):
            return True
        return False
    # end canMoveRow()

    def moveRow(self, where):
        if not self.canMoveRow(where):
            return
        row = None
        if ZMshtmlTableContext.ABOVE == where:
            row = self.tableDispEle.rows[self.rowDispEle.rowIndex - 1]
        else:
            row = self.tableDispEle.rows[self.rowDispEle.rowIndex + 1]
        self.rowDispEle.swapNode( getDispElement( row ) )
    # end moveRow()

    def canMoveCol(self, where):
        if self.rowDispEle and ZMshtmlTableContext.LEFT == where and self.cellDispEle.cellIndex > 0:
            return True
        elif self.rowDispEle and ZMshtmlTableContext.RIGHT == where and self.cellDispEle.cellIndex < (self.rowDispEle.cells.length - 1):
            return True
        return False
    # end canMovCol()

    def moveCol(self, where):
        if not self.canMoveCol(where):
            return

        cellIndex = self.cellDispEle.cellIndex
        newCellIndex = cellIndex + 1
        if ZMshtmlTableContext.LEFT == where:
            newCellIndex = cellIndex - 1
        numrows = self.tableDispEle.rows.length
        for r in range(numrows):
            row = self.tableDispEle.rows[r]
            getDispElement(row.cells[cellIndex]).swapNode(getDispElement(row.cells[newCellIndex]) )
    # end moveCol()

    def canInsertHeader(self): #@UnusedVariable
        return self.tableDispEle is not None
    # canInsertHeader()

    def insertHeader(self): #@UnusedVariable
        if not self.tableDispEle:
            return
        ncols = 2
        if self.tableDispEle.rows.length > 0:
            ncols = self.tableDispEle.rows[0].cells.length
        tHead =  self.tableDispEle.tHead
        if not tHead:
            tHead = self.tableDispEle.createTHead()
        row = getDispElement( tHead.insertRow(-1) )

        for idx in range(ncols): #@UnusedVariable
            th = row.ownerDocument.createElement(u"TH") #$NON-NLS-1$
            row.appendChild(th)
            th.innerText = u"TH" #$NON-NLS-1$
    # end insertHeader()

    def canInsertFooter(self): #@UnusedVariable
        return self.tableDispEle is not None
    # canInsertFooter()

    def insertFooter(self): #@UnusedVariable
        if not self.tableDispEle:
            return
        ncols = 2
        if self.tableDispEle.rows.length > 0:
            ncols = self.tableDispEle.rows[self.tableDispEle.rows.length-1].cells.length
        tFoot =  self.tableDispEle.tFoot
        if not tFoot:
            tFoot = self.tableDispEle.createTFoot()
        row = getDispElement( tFoot.insertRow(-1) )

        for idx in range(ncols): #@UnusedVariable
            cell = row.insertCell(-1)
            cell.innerText = u"FT" #$NON-NLS-1$
    # # end insertFooter()

    def canInsertCaption(self): #@UnusedVariable
        return self.tableDispEle is not None and self.tableDispEle.caption is None
    # canInsertCaption()

    def insertCaption(self): #@UnusedVariable
        if not self.tableDispEle:
            return
        caption = self.tableDispEle.caption
        if not caption:
            caption = self.tableDispEle.createCaption()
        getDispElement(caption).innerText = u"table caption" #$NON-NLS-1$
    # end insertCaption()

    def canDeleteRow(self):
        return self.rowDispEle is not None
    # canDeleteRow()

    def deleteRow(self):
        if not self.rowDispEle:
            return
        self.tableDispEle.deleteRow( self.rowDispEle.rowIndex )
    # end deleteRow()

    def canDeleteCol(self):
        return self.cellDispEle is not None
    # canDeleteCol()

    def deleteCol(self):
        if not self.cellDispEle:
            return
        cellIndex = self.cellDispEle.cellIndex
        numrows = self.tableDispEle.rows.length
        for r in range(numrows):
            row = self.tableDispEle.rows[r]
            getDispElement(row).deleteCell(cellIndex)
    # end deleteCol()

    def canClearCell(self):
        return self.cellDispEle is not None
    # canClearCell()

    def clearCell(self):
        if self.cellDispEle:
            self.cellDispEle.innerHTML = u"" #$NON-NLS-1$
    # end clearCell

# ZMshtmlTableContext

# ------------------------------------------------------------------------------
# table insertion and  edit contexts
# ------------------------------------------------------------------------------
class ZMshtmlEditControlTableContext(IZXHTMLEditControlTableContext):

    def __init__(self, mshtmlEditControl):
        self.mshtmlEditControl = mshtmlEditControl
    # end __init__()

    def _getTableElements(self, ele):
        # returns tuple (tableEle, rowEle, cellEle)
        tableEle = None
        rowEle = None
        cellEle = None
        if ele is None:
            ele = self.mshtmlEditControl._getMshtmlControl().getSelectedElement(True)
        if ele:
            while ele.tagName != u"TABLE" and ele.tagName != u"BODY": #$NON-NLS-1$ #$NON-NLS-2$
                #print "table ele=%s" % ele.tagName
                if not cellEle and (ele.tagName == u"TD" or ele.tagName == u"TH"): #$NON-NLS-1$ #$NON-NLS-2$
                    cellEle = ele
                if not rowEle and ele.tagName == u"TR": #$NON-NLS-1$
                    rowEle = ele
                ele = ele.parentElement
            if ele.tagName == u"TABLE": #$NON-NLS-1$
                tableEle = ele
        return (tableEle, rowEle, cellEle)
    # end _getTableElements()

    def _createTableContext(self, tableEle, rowEle, cellEle, parent):
        if not tableEle:
            return None
        table = None
        row = None
        cell = None
        if cellEle:
            cell = getDispElement(cellEle)
        if rowEle:
            row = getDispElement(rowEle)
        if tableEle:
            table = getDispElement(tableEle)
        return ZMshtmlTableContext(table, row, cell, parent)
    # end _createTableContext()

    def getTableContext(self):
        parentTableCtx = None
        # get table info under caret pos.
        (tableEle, rowEle, cellEle) = self._getTableElements(None)
        # get parent table if any.
        tableEle2 = None
        rowEle2 = None
        cellEle2 = None
        if tableEle is not None:
            (tableEle2, rowEle2, cellEle2) = self._getTableElements(tableEle.parentElement)
            parentTableCtx = self._createTableContext(tableEle2, rowEle2, cellEle2, None)
            tableCtx = self._createTableContext(tableEle, rowEle, cellEle, parentTableCtx)
            return tableCtx
        else:
            return None
    # end getTableContext

    def canInsertTable(self):
        return True
    # end canInsertTable()

    def canEditTable(self):
        return False
    # end canEditTable()

    def _getNoneAttr(self, attributes, attrName):
        if attributes and attributes.has_key(attrName):
            return attributes[attrName]
        else:
            return None
    # end _getNoneAttr()

    def insertTable(self, attributes):
        html = u"""<table """ #$NON-NLS-1$
        if self._getNoneAttr(attributes, u"border"): #$NON-NLS-1$
            html = html + u"""border="%s" """ % self._getNoneAttr(attributes, u"border") #$NON-NLS-1$ #$NON-NLS-2$
        if self._getNoneAttr(attributes, u"cellpadding"): #$NON-NLS-1$
            html = html + u"""cellpadding="%s" """ % self._getNoneAttr(attributes, u"cellpadding") #$NON-NLS-1$ #$NON-NLS-2$
        if self._getNoneAttr(attributes, u"cellspacing"): #$NON-NLS-1$
            html = html + u"""cellspacing="%s" """ % self._getNoneAttr(attributes, u"cellspacing") #$NON-NLS-1$ #$NON-NLS-2$
        if self._getNoneAttr(attributes, u"width"): #$NON-NLS-1$
            html = html + u"""width="%s" """ % self._getNoneAttr(attributes, u"width") #$NON-NLS-1$ #$NON-NLS-2$
        html = html + u">" #$NON-NLS-1$

        for row in range( int (attributes[u"rows"]) ): #$NON-NLS-1$ @UnusedVariable
            html = html + u"<tr>" #$NON-NLS-1$
            for col in range( int (attributes[u"cols"]) ): #$NON-NLS-1$ @UnusedVariable
                html = html + u"<td>  </td>" #$NON-NLS-1$
            html = html + u"</tr>" #$NON-NLS-1$
        html = html + u"</table>" #$NON-NLS-1$

        tr = self.mshtmlEditControl._getMshtmlControl().getSelectedTextRange(True)
        if tr:
            tr.pasteHTML(html)
        self.mshtmlEditControl._getMshtmlControl()._runStandardCleanupVisitors()
        self.mshtmlEditControl._getMshtmlControl()._fireContentModified()
    # end insertTable()

    def getTableAttributes(self):
        ctx = self.getTableContext()
        attrs = {}
        if ctx:
            if getNoneString(ctx.tableDispEle.border):
                attrs[u"border"] = ctx.tableDispEle.border #$NON-NLS-1$
            if getNoneString(ctx.tableDispEle.cellPadding):
                attrs[u"cellpadding"] = ctx.tableDispEle.cellPadding #$NON-NLS-1$
            if getNoneString(ctx.tableDispEle.cellSpacing):
                attrs[u"cellspacing"] = ctx.tableDispEle.cellSpacing #$NON-NLS-1$
            width = None
            if getNoneString(ctx.tableDispEle.width):
                width = ctx.tableDispEle.width #$NON-NLS-1$
            if getNoneString(ctx.tableDispEle.style.width):
                #style width attribute overrides top level table attribute.
                width = ctx.tableDispEle.style.width #$NON-NLS-1$                
            if width:
                attrs[u"width"] = width #$NON-NLS-1$
        return attrs
    # end getTableAttributes()

    def setTableAttributes(self, attributes):
        ctx = self.getTableContext()
        if not ctx:
            return
        if self._getNoneAttr(attributes, u"border"): #$NON-NLS-1$
            ctx.tableDispEle.border = self._getNoneAttr(attributes, u"border") #$NON-NLS-1$
        if self._getNoneAttr(attributes, u"cellpadding"): #$NON-NLS-1$
            ctx.tableDispEle.cellPadding = self._getNoneAttr(attributes, u"cellpadding") #$NON-NLS-1$
        if self._getNoneAttr(attributes, u"cellspacing"): #$NON-NLS-1$
            ctx.tableDispEle.cellSpacing = self._getNoneAttr(attributes, u"cellspacing") #$NON-NLS-1$
        if self._getNoneAttr(attributes, u"width"): #$NON-NLS-1$
            if getNoneString(ctx.tableDispEle.style.width):
                # also set the css style attr width if one existed.
                ctx.tableDispEle.style.width = self._getNoneAttr(attributes, u"width") #$NON-NLS-1$
            ctx.tableDispEle.width = self._getNoneAttr(attributes, u"width") #$NON-NLS-1$                
        self.mshtmlEditControl._getMshtmlControl()._runStandardCleanupVisitors()
        self.mshtmlEditControl._getMshtmlControl()._fireContentModified()
    # end setTableAttributes()

    def isCommandEnabled(self, commandId):
        ctx = self.getTableContext()
        if ctx:
            if IZXHTMLEditControlTableContext.INSERT_ROW_ABOVE == commandId:
                return ctx.canInsertRow(ZMshtmlTableContext.ABOVE)
            elif IZXHTMLEditControlTableContext.INSERT_ROW_BELOW == commandId:
                return ctx.canInsertRow(ZMshtmlTableContext.BELOW)

            elif IZXHTMLEditControlTableContext.INSERT_COL_LEFT == commandId:
                return ctx.canInsertCol(ZMshtmlTableContext.LEFT)
            elif IZXHTMLEditControlTableContext.INSERT_COL_RIGHT == commandId:
                return ctx.canInsertCol(ZMshtmlTableContext.RIGHT)

            elif IZXHTMLEditControlTableContext.MOVE_ROW_ABOVE == commandId:
                return ctx.canMoveRow(ZMshtmlTableContext.ABOVE)
            elif IZXHTMLEditControlTableContext.MOVE_ROW_BELOW == commandId:
                return ctx.canMoveRow(ZMshtmlTableContext.BELOW)

            elif IZXHTMLEditControlTableContext.MOVE_COL_LEFT == commandId:
                return ctx.canMoveCol(ZMshtmlTableContext.LEFT)
            elif IZXHTMLEditControlTableContext.MOVE_COL_RIGHT == commandId:
                return ctx.canMoveCol(ZMshtmlTableContext.RIGHT)

            elif IZXHTMLEditControlTableContext.DELETE_ROW == commandId:
                return ctx.canDeleteRow()
            elif IZXHTMLEditControlTableContext.DELETE_COL == commandId:
                return ctx.canDeleteCol()
            elif IZXHTMLEditControlTableContext.CLEAR_CELL == commandId:
                return ctx.canClearCell()

            elif IZXHTMLEditControlTableContext.INSERT_HEADER == commandId:
                return ctx.canInsertHeader()
            elif IZXHTMLEditControlTableContext.INSERT_FOOTER == commandId:
                return ctx.canInsertFooter()
            elif IZXHTMLEditControlTableContext.INSERT_CAPTION == commandId:
                return ctx.canInsertCaption()


            elif IZXHTMLEditControlTableContext.EDIT_TABLE_ATTRS == commandId:
                return True

        # default
        return IZXHTMLEditControlTableContext.INSERT_TABLE == commandId
    # end isCommandEnabled()

    def execCommand(self, commandId):
        ctx = self.getTableContext()
        handled = True
        if ctx:
            if IZXHTMLEditControlTableContext.INSERT_ROW_ABOVE == commandId:
                ctx.insertRow(ZMshtmlTableContext.ABOVE)
            elif IZXHTMLEditControlTableContext.INSERT_ROW_BELOW == commandId:
                ctx.insertRow(ZMshtmlTableContext.BELOW)
            elif IZXHTMLEditControlTableContext.INSERT_COL_LEFT == commandId:
                ctx.insertCol(ZMshtmlTableContext.LEFT)
            elif IZXHTMLEditControlTableContext.INSERT_COL_RIGHT == commandId:
                ctx.insertCol(ZMshtmlTableContext.RIGHT)

            elif IZXHTMLEditControlTableContext.MOVE_ROW_ABOVE == commandId:
                ctx.moveRow(ZMshtmlTableContext.ABOVE)
            elif IZXHTMLEditControlTableContext.MOVE_ROW_BELOW == commandId:
                ctx.moveRow(ZMshtmlTableContext.BELOW)

            elif IZXHTMLEditControlTableContext.MOVE_COL_LEFT == commandId:
                ctx.moveCol(ZMshtmlTableContext.LEFT)
            elif IZXHTMLEditControlTableContext.MOVE_COL_RIGHT == commandId:
                ctx.moveCol(ZMshtmlTableContext.RIGHT)

            elif IZXHTMLEditControlTableContext.DELETE_ROW == commandId:
                ctx.deleteRow()
            elif IZXHTMLEditControlTableContext.DELETE_COL == commandId:
                ctx.deleteCol()
            elif IZXHTMLEditControlTableContext.CLEAR_CELL == commandId:
                ctx.clearCell()

            elif IZXHTMLEditControlTableContext.INSERT_HEADER == commandId:
                ctx.insertHeader()
            elif IZXHTMLEditControlTableContext.INSERT_FOOTER == commandId:
                ctx.insertFooter()
            elif IZXHTMLEditControlTableContext.INSERT_CAPTION == commandId:
                ctx.insertCaption()
            else:
                handled = False

        if handled:
            self.mshtmlEditControl._getMshtmlControl()._runStandardCleanupVisitors()
            self.mshtmlEditControl._getMshtmlControl()._fireContentModified()
    # end execCommand()

# end ZMshtmlEditControlTableContext
