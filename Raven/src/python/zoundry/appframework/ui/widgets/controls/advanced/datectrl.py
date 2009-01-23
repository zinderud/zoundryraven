from wx.lib.masked.ctrl import Ctrl
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.events.datectrlevents import ZDateChangeEvent
from zoundry.appframework.ui.widgets.controls.common.imgbutton import ZImageButton
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.base.util.dateutil import createSchemaDateTime
from zoundry.base.util.schematypes import ZSchemaDateTime
import re
import wx #@UnusedImport
import wx.calendar #@Reimport

# Date Tuple index constants
YEAR = 0
MONTH = 1
DAY = 2
HOUR = 3
MINUTE = 4
AMPM = 5


# ------------------------------------------------------------------------------
# This class implements a popup window that is used to select a time from a 
# Calendar Widget.
# ------------------------------------------------------------------------------
class ZCalendarPopupWindow(wx.PopupTransientWindow):

    def __init__(self, parent, dateTuple, resetDateTuple = None):
        self.parent = parent
        self.dateTuple = dateTuple
        self.resetDateTuple = resetDateTuple
        
        wx.PopupTransientWindow.__init__(self, parent, style = wx.SIMPLE_BORDER)
        
        self._createWidgets()
        self._populateWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
        
        self.SetSize(self.GetBestSize())
        self.Layout()
    # end __init__()
    
    def getDateTuple(self):
        return self.dateTuple
    # end getDateTuple()
    
    def _createWidgets(self):
        wxDt = self._wxDateFromDateTuple(self.dateTuple)
        self.calendar = wx.calendar.CalendarCtrl(self, wx.ID_ANY, wxDt, style = wx.calendar.CAL_SHOW_HOLIDAYS | wx.calendar.CAL_SUNDAY_FIRST | wx.calendar.CAL_BORDER_ROUND | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION | wx.SIMPLE_BORDER)
        self.nowButton = wx.Button(self, wx.ID_ANY, _extstr(u"datectrl.Now")) #$NON-NLS-1$
        self.resetButton = wx.Button(self, wx.ID_ANY, _extstr(u"datectrl.Reset")) #$NON-NLS-1$
    # end _createWidgets()
    
    def _populateWidgets(self):
        if self.resetDateTuple is None:
            self.resetButton.Show(False)
    # end _populateWidgets()
    
    def _layoutWidgets(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.nowButton, 0, wx.EXPAND | wx.ALL, 3)
        vbox.Add(self.resetButton, 0, wx.EXPAND | wx.ALL, 3)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.calendar, 0, wx.EXPAND | wx.ALL, 2)
        hbox.AddSizer(vbox, 0, wx.EXPAND | wx.ALL, 2)

        self.SetSizer(hbox)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()
    
    def _bindWidgetEvents(self):
        self.Bind(wx.calendar.EVT_CALENDAR, self.onCalendar, self.calendar)
        self.Bind(wx.EVT_BUTTON, self.onNow, self.nowButton)
        self.Bind(wx.EVT_BUTTON, self.onReset, self.resetButton)
    # end _bindWidgetEvents()
    
    def onCalendar(self, event):
        wxDT = self.calendar.GetDate()
        self.dateTuple = self._dateTupleFromWxDate(wxDT)
        self.Dismiss()
        self.parent.onCalendarPopup(self.dateTuple)
        event.Skip()
    # end onCalendar()
    
    def onNow(self, event):
        self.calendar.SetDate(self._wxDateFromDateTuple(None))
        event.Skip()
    # end onNow()
    
    def onReset(self, event):
        if self.resetDateTuple is not None:
            self.calendar.SetDate(self._wxDateFromDateTuple(self.resetDateTuple))
        event.Skip()
    # end onReset()
    
    def _dateTupleFromWxDate(self, wxDT):
        return (wxDT.GetYear(), wxDT.GetMonth() + 1, wxDT.GetDay())
    # end _zSchemaDateTimeFromWxDate()
    
    def _wxDateFromDateTuple(self, tuple):
        if tuple is None:
            return wx.DateTime_Now()
        return wx.DateTimeFromDMY(tuple[DAY], tuple[MONTH] - 1, tuple[YEAR], 0, 0, 0, 0)
    # end _wxDateFromZSchemaDateTime()

# end ZCalendarPopupWindow


# FIXME (EPW) support euro formatted dates


DATE_TIME_PATTERN = re.compile(u"(\\d\\d)/(\\d\\d)/(\\d\\d\\d\\d) (\\d\\d):(\\d\\d) (..)") #$NON-NLS-1$


# ------------------------------------------------------------------------------
# A control that lets the user select/configure a date and time.  This control
# accepts a ZSchemaDateTime object as its input and returns a ZSchemaDateTime
# object as its output (via getDateTime()).
# ------------------------------------------------------------------------------
class ZDateTimeChooser(ZTransparentPanel):

    FORMAT_US = u"USDATETIMEMMDDYYYY/HHMM" #$NON-NLS-1$

    def __init__(self, parent, dateTime = None, resetTime = None):
        self.resetTuple = self._getDateTupleFromSchemaDateTime(resetTime)
        self.dateTimeFormatType = ZDateTimeChooser.FORMAT_US
        
        ZTransparentPanel.__init__(self, parent, wx.ID_ANY)

#        df = (u"blogui.wx_datecontrol") #$NON-NLS-1$
#        if df and df.lower().strip() == u"ddmmyyyy": #$NON-NLS-1$
#            self.dateFormatType = ZDateTimeChooser.FORMAT_DDMMYYYY
#        elif df and df.lower().strip() == u"yyyymmdd": #$NON-NLS-1$
#            self.dateFormatType = ZDateTimeChooser.FORMAT_YYYYMMDD

        self._createWidgets()
        self._populateWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
        
        self.setDateTime(dateTime)
    # end __init__()

    def Enable(self, enabledFlag = True):
        self.dateTimeControl.Enable(enabledFlag)
        self.calendarButton.Show(enabledFlag)
        self.Layout()
    # end Enable()

    def _getDateTupleFromSchemaDateTime(self, dateTime):
        if dateTime is None:
            return None
        pyDT = dateTime.getDateTime(True)
        return (pyDT.year, pyDT.month, pyDT.day)
    # end _getDateTupleFromSchemaDateTime()
    
    def _getRawDateTimeTuple(self):
        m = re.match(DATE_TIME_PATTERN, self.dateTimeControl.GetValue())
        if m:
            (month, day, year, h, m, pm) = m.groups()
            return (year, month, day, h, m, pm)
        else:
            return None
    # end _getRawDateTimeTuple()
    
    def getDateTimeTuple(self):
        rawTuple = self._getRawDateTimeTuple()
        if rawTuple is not None:
            h = int(rawTuple[HOUR])
            ampm = rawTuple[AMPM]
            if ampm == u"AM" and h == 12: #$NON-NLS-1$
                h = 0
            if ampm == u"PM" and not h == 12: #$NON-NLS-1$
                h += 12
            return (int(rawTuple[YEAR]), int(rawTuple[MONTH]), int(rawTuple[DAY]), h, int(rawTuple[MINUTE]))
        else:
            return None
    # end getDateTimeTuple()
    
    def getDateTime(self):
        dtTuple = self.getDateTimeTuple()
        if dtTuple is not None:
            return createSchemaDateTime(dtTuple[YEAR], dtTuple[MONTH], dtTuple[DAY], dtTuple[HOUR], dtTuple[MINUTE], 0, True)
        else:
            return None
    # end getDateTime()
    
    def setDateTime(self, dateTime):
        # Stop listening to text events until after we are done setting the value
        self.Unbind(wx.EVT_TEXT, self.dateTimeControl)
        if dateTime is None:
            dateTime = ZSchemaDateTime()
        dtStr = dateTime.toString(u"%m/%d/%Y %I:%M %p", True) #$NON-NLS-1$
        self.dateTimeControl.SetValue(dtStr)
        self.Bind(wx.EVT_TEXT, self.onDateTimeText, self.dateTimeControl)
    # end setDateTime()

    def _createWidgets(self):
        registry = getResourceRegistry()
        self.calendarBitmap = registry.getBitmap(u"images/widgets/dateTime/calendar.png") #$NON-NLS-1$
        
        self.dateTimeControl = Ctrl(self, wx.ID_ANY, u"", autoformat=self.dateTimeFormatType, demo=False, emptyInvalid=True, name=u'dateTime') #$NON-NLS-1$ #$NON-NLS-2$
        self.calendarButton = ZImageButton(self, self.calendarBitmap, True, None, True)
    # end _createWidgets()
    
    def _populateWidgets(self):
        pass
    # end _bindWidgetEvents()
    
    def _layoutWidgets(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.dateTimeControl, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        hbox.Add(self.calendarButton, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        self.SetSizer(hbox)
        self.SetAutoLayout(True)
    # end _layoutWidgets()
    
    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_TEXT, self.onDateTimeText, self.dateTimeControl)
        self.Bind(wx.EVT_BUTTON, self.onCalendarButton, self.calendarButton)
    # end _bindWidgetEvents()
    
    def onDateTimeText(self, event):
        if self.dateTimeControl.IsValid():
            self._fireDateChangeEvent()

        event.Skip()
    # end onDateTimeText()
    
    def onCalendarButton(self, event):
        dtTuple = self.getDateTimeTuple()
        dateTuple = (dtTuple[YEAR], dtTuple[MONTH], dtTuple[DAY])
        popup = ZCalendarPopupWindow(self, dateTuple, self.resetTuple)

        ctrl = self.dateTimeControl
        pos = ctrl.ClientToScreen( (0,0) )
        buttonSize =  ctrl.GetSize()
        popup.Position(pos, (0, buttonSize[1]))

        popup.Popup()
        event.Skip()
    # end onCalendarButton()
    
    def onCalendarPopup(self, dateTuple):
        (year, month, day, hour, minute, ampm) = self._getRawDateTimeTuple() #@UnusedVariable
        year = dateTuple[YEAR]
        month = dateTuple[MONTH]
        day = dateTuple[DAY]
        newValue = u"%02d/%02d/%04d %s:%s %s" % (month, day, year, hour, minute, ampm) #$NON-NLS-1$
        self.dateTimeControl.SetValue(newValue)
        self._fireDateChangeEvent()
    # end onCalendarPopup()
    
    def _fireDateChangeEvent(self):
        event = ZDateChangeEvent(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireDateChangeEvent()

# end ZDateTimeChooser
