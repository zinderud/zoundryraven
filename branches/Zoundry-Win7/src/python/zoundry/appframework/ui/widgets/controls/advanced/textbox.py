from wx._controls import wxEVT_COMMAND_TEXT_ENTER
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.events.advtextbox import ZAdvTextBoxOptionEvent
from zoundry.appframework.ui.util.colorutil import getDefaultControlBackgroundColor
from zoundry.appframework.ui.util.colorutil import getDefaultControlBorderColor
from zoundry.appframework.ui.util.fontutil import getTextDimensions
from zoundry.appframework.ui.widgets.controls.common.bitmap import ZStaticBitmap
from zoundry.appframework.ui.widgets.controls.common.imgbutton import ZImageButton
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZMenuModel
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
import wx

# --------------------------------------------------------------------------------------
# Action that fires when the user selects one of the choices.
# --------------------------------------------------------------------------------------
class ZTextBoxChoiceAction(ZMenuAction):

    def __init__(self, choiceId):
        self.choiceId = choiceId
        ZMenuAction.__init__(self)
    # end __init__()

    def isChecked(self, actionContext): #@UnusedVariable
        textBox = actionContext.getParentWindow()
        choices = textBox.selectedChoices
        return self.choiceId in choices
    # end isChecked()

    def runAction(self, actionContext): #@UnusedVariable
        pass
    # end runAction()

    def runCheckAction(self, actionContext, checked):
        textBox = actionContext.getParentWindow()
        if checked:
            textBox.onChoice(self.choiceId)
        else:
            textBox.onUnChoice(self.choiceId)
    # end runCheckAction()
    
# end ZTextBoxChoiceAction



# --------------------------------------------------------------------------------------
# Custom text box control.  This control works just like a normal text control,
# except that it also displays a list of items when the image at the front of
# the control is clicked.
#
# This control emits the standard WX text control events, such as EVT_TEXT.  In
# addition, it has the following custom events:
#
# ZEVT_ATB_OPTION_SELECTED: this event is fired when the user selects an option
#                           from the list of options (when the image button is pressed)
#
# Note that the class is constructed with a list of tuples that define the choices
# that should be displayed by the control's dropdown.  The format of the tuple should
# be:  (label, bitmap, id).  When the user makes a selection, the above event is
# fired, with the ID in the event set to the id of the choice.
#
# Note also that, when configured for multiple selction, the bitmap for each choice is
# ignored (since we can't display both a bitmap and a checkbox for a given menu item).
# --------------------------------------------------------------------------------------
class ZAdvancedTextBox(wx.Panel):

    def __init__(self, parent, bitmap, choices, multiSelect = False):
        self.bitmap = bitmap
        self.choices = choices
        self.selectedChoices = []
        self.multiSelect = multiSelect
        self.backgroundColor = getDefaultControlBackgroundColor()
        self.borderColor = getDefaultControlBorderColor()

        wx.Panel.__init__(self, parent, wx.ID_ANY, style = wx.NO_BORDER)
        
        self.SetBackgroundColour(self.backgroundColor)

        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def GetValue(self):
        return self.textBox.GetValue()
    # end GetValue()

    def SetValue(self, value):
        self.textBox.SetValue(value)
    # end SetValue()
    
    def SetToolTipString(self, tooltip):
        self.textBox.SetToolTipString(tooltip)
    # end SetToolTipString()

    def setCurrentChoice(self, choiceId):
        self.selectedChoices = [choiceId]
    # end setCurrentChoice()
    
    def setCurrentChoices(self, choiceIds):
        self.selectedChoices = choiceIds
    # end setCurrentChoices()
    
    def getCurrentChoice(self):
        if self.multiSelect:
            raise ZAppFrameworkException(u"Attempted to get a single choice from an advanced text box configured for multiple selection.") #$NON-NLS-1$
        if self.selectedChoices:
            return self.selectedChoices[0]
        return None
    # end getCurrentChoice()
    
    def getCurrentChoices(self):
        if not self.multiSelect:
            raise ZAppFrameworkException(u"Attempted to get multiple choices from an advanced text box configured for single selection.") #$NON-NLS-1$
        return self.selectedChoices
    # end getCurrentChoice()

    def _createWidgets(self):
        self.textBox = wx.TextCtrl(self, wx.ID_ANY, style = wx.NO_BORDER | wx.TE_PROCESS_ENTER)
        hasChoices = len(self.choices) > 1
        self.bitmapButton = ZImageButton(self, self.bitmap, hasChoices, None, hasChoices)
        self.staticBitmap = ZStaticBitmap(self, self.bitmap)
        self.clearButton = self._createClearButton()
        self._createChoiceMenu()
    # end _createWidgets()
    
    def _createChoiceMenu(self):
        menuModel = self._createChoiceMenuModel()
        menuContext = ZMenuActionContext(self)
        contentProvider = ZModelBasedMenuContentProvider(menuModel, menuContext)
        eventHandler = ZModelBasedMenuEventHandler(menuModel, menuContext)
        self.menu = ZMenu(self, menuModel.getRootNode(), contentProvider, eventHandler)
    # end _createChoiceMenu()
    
    def _createChoiceMenuModel(self):
        model = ZMenuModel()
        for (label, bitmap, id) in self.choices:
            action = ZTextBoxChoiceAction(id)
            menuId = model.addMenuItemWithAction(label, 0, action)
            model.setMenuItemCheckbox(menuId, True)
            model.setMenuItemBitmap(menuId, bitmap)
        return model
    # end _createChoiceMenuModel()
    
    def _createClearButton(self):
        registry = getResourceRegistry()
        clearBmp = registry.getBitmap(u"images/widgets/textbox/clear.png") #$NON-NLS-1$
        clearHoverBmp = registry.getBitmap(u"images/widgets/textbox/clear-hover.png") #$NON-NLS-1$
        return ZImageButton(self, clearBmp, False, clearHoverBmp, False)
    # end _createClearButton()
    
    def _layoutWidgets(self):
        (w, h) = getTextDimensions(u"Zoundry", self.textBox) #$NON-NLS-1$ @UnusedVariable
        self.textBox.SetSizeHints(-1, h + 2)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.staticBitmap, 0, wx.ALIGN_CENTER | wx.RIGHT | wx.LEFT, 3)
        box.Add(self.bitmapButton, 0, wx.ALIGN_CENTER | wx.RIGHT | wx.LEFT, 3)
        box.Add( (3, -1) )
        box.Add(self.textBox, 1, wx.EXPAND | wx.TOP, 3)
        box.Add(self.clearButton, 0, wx.ALIGN_CENTER | wx.RIGHT | wx.LEFT, 3)
        
        self.clearButton.Show(False)
        if self.choices is None or len(self.choices) == 0:
            self.staticBitmap.Show(True)
            self.bitmapButton.Show(False)
        else:
            self.staticBitmap.Show(False)
            self.bitmapButton.Show(True)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(box, 1, wx.EXPAND | wx.ALL, 2)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end _layoutWidgets()
    
    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
        self.Bind(wx.EVT_BUTTON, self.onButtonClicked, self.bitmapButton)
        self.Bind(wx.EVT_TEXT, self.onText, self.textBox)
        self.Bind(wx.EVT_TEXT_ENTER, self.onPropagateEvent, self.textBox)
        self.Bind(wx.EVT_BUTTON, self.onClearButtonClicked, self.clearButton)
    # end _bindWidgetEvents()
    
    def onButtonClicked(self, event):
        if len(self.choices) > 1:
            (w, h) = self.GetSizeTuple() #@UnusedVariable
            pos = wx.Point(1, h - 2)
            self.menu.refresh()
            self.PopupMenu(self.menu, pos)
        event.Skip
    # end onButtonClicked()
    
    def onClearButtonClicked(self, event):
        self.SetValue(u"") #$NON-NLS-1$
        self.clearButton.Show(False)
        txtEvent = wx.CommandEvent(wxEVT_COMMAND_TEXT_ENTER, self.GetId())
        self.GetEventHandler().AddPendingEvent(txtEvent)
        event.Skip()
    # end onClearButtonClicked()

    def onText(self, event):
        if self.clearButton.IsShown() and not self.textBox.GetValue():
            self.clearButton.Show(False)
            self.Layout()
        elif not self.clearButton.IsShown() and self.textBox.GetValue():
            self.clearButton.Show(True)
            self.Layout()
        self.onPropagateEvent(event)
    # end onText()

    def onPropagateEvent(self, event):
        # Propagate the event
        event = event.Clone()
        event.SetId(self.GetId())
        self.GetEventHandler().AddPendingEvent(event) 
    # end onPropagateEvent()
    
    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        (width, height) = self.GetSizeTuple()
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE), wx.SOLID))
        paintDC.Clear()

        # Draw the background white
        brush = wx.Brush(self.backgroundColor)
        paintDC.SetPen(wx.Pen(self.borderColor, 1, wx.SOLID))
        paintDC.SetBrush(brush)
        paintDC.DrawRectangle(0, 0, width, height)
        
        del paintDC
        event.Skip()
    # end onPaint
    
    def onChoice(self, choiceId):
        # Update the internal selection state.
        if self.multiSelect:
            if not choiceId in self.selectedChoices:
                self.selectedChoices.append(choiceId)
        else:
            self.selectedChoices = [choiceId]

        event = ZAdvTextBoxOptionEvent(self.GetId(), choiceId)
        self.GetEventHandler().AddPendingEvent(event)
    # end onChoice()

    def onUnChoice(self, choiceId):
        if choiceId in self.selectedChoices:
            self.selectedChoices.remove(choiceId)
    # end onChoice()

# end ZAdvancedTextBox
