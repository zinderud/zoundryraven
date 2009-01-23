from zoundry.base.util.urlutil import getFilePathFromUri
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.events.validation import ZWidgetInvalidEvent
from zoundry.appframework.ui.events.validation import ZWidgetValidEvent
from zoundry.appframework.ui.widgets.controls.common.imgbutton import ZNoFocusImageButton
import re
import string
import wx
import os.path

# -------------------------------------------------------------------------------------
# The interface for a validating control's validator.  All validating controls require
# a validator in order to work properly.
# -------------------------------------------------------------------------------------
class IZControlValidator:

    def isValid(self, value):
        u"Returns True if the value is valid, False if it is not." #$NON-NLS-1$
    # end isValid()

    def getInvalidReason(self):
        u"Returns the reason (a string) why the last call to isValid() returned False." #$NON-NLS-1$
    # end getInvalidReason()

# end IZControlValidator


# -------------------------------------------------------------------------------------
# Base class for validators.  This base class has a member variable called 'reason'
# and handles managing it.
# -------------------------------------------------------------------------------------
class ZBaseControlValidator(IZControlValidator):
    
    def __init__(self):
        self.reason = u"" #$NON-NLS-1$
    # end __init__()

    def _setReason(self, reason):
        self.reason = reason
        return False
    # end setReason()

    def isValid(self, value):
        rval = self._isValid(value.strip())
        if rval:
            self.reason = u"" #$NON-NLS-1$
        return rval
    # end isValid()
    
    def _isValid(self, value):
        u"Subclasses should override this." #$NON-NLS-1$
    # end _isValid()
    
    def getInvalidReason(self):
        return self.reason
    # end getInvalidReason()

# end ZBaseControlValidator


# -------------------------------------------------------------------------------------
# Null control validator - always validates to True.
# -------------------------------------------------------------------------------------
class ZNullControlValidator(ZBaseControlValidator):

    def __init(self):
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def _isValid(self, value): #@UnusedVariable
        return True
    # end isValid()

# end ZNullControlValidator


# -------------------------------------------------------------------------------------
# Regular expression based control validator.
# -------------------------------------------------------------------------------------
class ZRegexpControlValidator(ZBaseControlValidator):
    
    def __init__(self, regexp, errorMessage):
        self.regexp = re.compile(regexp)
        self.errorMessage = errorMessage
        ZBaseControlValidator.__init__(self)
    # end __init__()
    
    def _isValid(self, value): #@UnusedVariable
        m = self.regexp.match(value)
        if not m:
            return self._setReason(self.errorMessage)
        return True
    # end isValid()

# end ZRegexpControlValidator


# -------------------------------------------------------------------------------------
# A simple validator that ensures that the control has a non-empty value.
# -------------------------------------------------------------------------------------
class ZNonEmptySelectionValidator(ZBaseControlValidator):

    def __init__(self, errorMessage):
        self.errorMessage = errorMessage
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def _isValid(self, value):
        if not value:
            return self._setReason(self.errorMessage)

        return True
    # end _isValid()

# end ZNonEmptySelectionValidator

# Pattern to match http, https, ftp protocol -> scheme:/paths
URL_RE_PATTERN = r"(^|[ \t\r\n])((\w+):(([A-Za-z0-9$_.+!*(),;/?:@&~=-])|%[A-Fa-f0-9]{2}){2,}(#([a-zA-Z0-9][a-zA-Z0-9$_.+!*(),;/?:@&~=%-]*))?([A-Za-z0-9$_+!*();/?:~-]))" #$NON-NLS-1$
URL_RE = re.compile(URL_RE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# Pattern to match http, https, ftp and file protocol
FILEURL_RE_PATTERN = r"(^|[ \t\r\n])((ftp|http|https|file):(([A-Za-z0-9$_.+!*(),;/?:@&~=-])|%[A-Fa-f0-9]{2}){2,}(#([a-zA-Z0-9][a-zA-Z0-9$_.+!*(),;/?:@&~=%-]*))?([A-Za-z0-9$_+!*();/?:~-]))" #$NON-NLS-1$
FILEURL_RE = re.compile(FILEURL_RE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# Simple pattern to match local hard drive paths. Eg. C:/temp. or network path i.e. \\share\path
FILE_RE_PATTERN = r"((\w:)|(\\))([\\\/])[_A-Za-z0-9]+"  #$NON-NLS-1$
FILE_RE = re.compile(FILE_RE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# -------------------------------------------------------------------------------------
# A validator that ensures that the control has a url like value.
# (Does not support file:// protocol).
# -------------------------------------------------------------------------------------
class ZUrlSelectionValidator(ZBaseControlValidator):

    def __init__(self, errorMessage, nonEmpty=True):
        # if nonEmpty is false, then empty value is also valid (e.g. url field is optional)
        self.errorMessage = errorMessage
        self.nonEmpty = nonEmpty
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def _isValid(self, value):
        message = self.errorMessage
        valid = False
        if not value and not self.nonEmpty:            
            valid = True
        elif value:
            value = value.strip().lower()
            (valid, message) = self._validateProtocol(value, message)
        if not valid:
            return self._setReason(message)
        return valid
    # end _isValid()
    
    def _validateProtocol(self, value, message):
        # validate procotol in given value and return tuple (bool, message)
        valid = False
        if URL_RE.match(value) is not None:
            valid = True
        return (valid, message)
    # end _validateProtocol()
# end ZUrlSelectionValidator

# -------------------------------------------------------------------------------------
# A validator that ensures that the control has a url like value.
# as well as validates that local file location path exists
# if protocol is file://
# -------------------------------------------------------------------------------------
class ZFileUrlSelectionValidator(ZUrlSelectionValidator):
    def __init__(self, errorMessage, nonEmpty=True):
        ZUrlSelectionValidator.__init__(self, errorMessage, nonEmpty)
    # end __init()__
    
    def _validateProtocol(self, value, message):
        # validate procotol in given value and return tuple (bool, message)
        valid = False
        if FILEURL_RE.match(value) is not None:
            valid = True
        filepath = None
        # if file://, then validate path.
        if valid and value.lower().startswith(u"file:"): #$NON-NLS-1$
            filepath = getFilePathFromUri(value)
            valid = os.path.exists(filepath)
            if not valid:
                message = message + u"(invalid file path)" #$NON-NLS-1$
        elif not valid and FILE_RE.match(value) is not None:
            # user typed in local path, eg c:/temp.
            valid = os.path.exists(value)
            if not valid:
                message = message + u"(invalid file path)" #$NON-NLS-1$
        return (valid, message)
    # end _validateProtocol()    
# end ZFileUrlSelectionValidator

# -------------------------------------------------------------------------------------
# A validator that ensures that the control has an integer value.
# -------------------------------------------------------------------------------------
class ZIntegerSelectionValidator(ZBaseControlValidator):
    
    ALLOW_EMPTY = 1
    ALLOW_ZERO = 2
    POSITIVE_ONLY = 4
    NEGATIVE_ONLY = 8

    def __init__(self, errorMessage = None, flags=0):
        self.errorMessage = errorMessage
        self.setFlags(flags)
        if self.errorMessage is None:
            self.errorMessage = _extstr(u"validatingctrl.InvalidIntegerErrorMessage") #$NON-NLS-1$
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def setFlags(self, flags):
        self.flags = flags 
    # end setFlags()

    def _isValid(self, value):
        valid = False
        if (not value or value.strip() == u"") and (self.flags & ZIntegerSelectionValidator.ALLOW_EMPTY) == ZIntegerSelectionValidator.ALLOW_EMPTY: #$NON-NLS-1$
            valid = True        
        elif value:
            try:
                intval = string.atoi(value.strip())
                valid = True
                if (self.flags & ZIntegerSelectionValidator.POSITIVE_ONLY) == ZIntegerSelectionValidator.POSITIVE_ONLY and intval <= 0:
                    valid = False
                if (self.flags & ZIntegerSelectionValidator.NEGATIVE_ONLY) == ZIntegerSelectionValidator.NEGATIVE_ONLY and intval >= 0:
                    valid = False
                if not valid and (self.flags & ZIntegerSelectionValidator.ALLOW_ZERO) == ZIntegerSelectionValidator.ALLOW_ZERO and intval == 0:
                    valid = True                        
            except:
                valid = False
        if not valid:
            return self._setReason(self.errorMessage)
        return valid
    # end _isValid()

# end ZIntegerSelectionValidator


# -------------------------------------------------------------------------------------
# CSS length validator
# A validator that ensures that the control has a positive integer value with an optional
# trailing units px or em.
# -------------------------------------------------------------------------------------

CSS_LENGTH_PATTERN = r"^(\d+\.?\d*(%|in|cm|mm|em|pt|pc|px)*)$" #$NON-NLS-1$
CSS_LENGTH_RE = re.compile(CSS_LENGTH_PATTERN, re.IGNORECASE |re.UNICODE | re.DOTALL)

class ZCssLengthSelectionValidator(ZBaseControlValidator):
    
    ALLOW_EMPTY = 1

    def __init__(self, errorMessage = None,  flags=0):
        self.errorMessage = errorMessage
        self.setFlags(flags)
        if self.errorMessage is None:
            self.errorMessage = _extstr(u"validatingctrl.CssLengthErrorMessage") #$NON-NLS-1$
        ZBaseControlValidator.__init__(self)
    # end __init__()
    
    def setFlags(self, flags):
        self.flags = flags 
    # end setFlags()
    
    def _isValid(self, value):
        valid = False
        if (not value or value.strip() == u"") and (self.flags & ZCssLengthSelectionValidator.ALLOW_EMPTY) == ZCssLengthSelectionValidator.ALLOW_EMPTY: #$NON-NLS-1$
            valid = True        
        elif value:
            valid = CSS_LENGTH_RE.match(value.strip())
        if not valid:
            return self._setReason(self.errorMessage)
        return valid
    # end _isValid()

# end ZUrlSelectionValidator



# -------------------------------------------------------------------------------------
# Interface implemented by validating controls.
# -------------------------------------------------------------------------------------
class IZValidatingCtrl:

    def validate(self):
        u"Validates the widget.  An event may be fired as a result." #$NON-NLS-1$
    # end validate()
    
# end IZValidatingCtrl


# -------------------------------------------------------------------------------------
# Base class for all Zoundry validating controls.  A validating control consists of
# some standard/common control (like a TextCtrl) along with a static image.  The static
# image will be shown or hidden based on whether the input is valid or not.  In 
# addition, validating controls will fire events for when the control becomes valid
# or when it becomes invalid.
# -------------------------------------------------------------------------------------
class ZValidatingCtrl(wx.Panel, IZValidatingCtrl):

    def __init__(self, validator, parent):
        self.validator = validator
        self.resourceRegistry = getResourceRegistry()
        self.isValid = True
        
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
        self._validateWidget()
    # end __init__()
    
    def validate(self):
        u"Public method that can be called to validate the widget." #$NON-NLS-1$
        self._validateWidget()
    # end validate()

    def _createWidgets(self):
        bitmap = self.resourceRegistry.getBitmap(u"images/widgets/validation/invalid.png") #$NON-NLS-1$
        hoverBitmap = self.resourceRegistry.getBitmap(u"images/widgets/validation/invalid_hover.png") #$NON-NLS-1$
        self.warningImage = ZNoFocusImageButton(self, bitmap, False, hoverBitmap, False, style = wx.NO_BORDER | wx.TAB_TRAVERSAL)
        # Assume widget is valid - we'll check that later.
        self.warningImage.Show(False)
        self.widget = self._createWidget()
    # end _createWidgets()

    def _layoutWidgets(self):
        boxSizer = wx.BoxSizer(wx.HORIZONTAL)
        boxSizer.Add(self.warningImage, 0, wx.ALIGN_CENTER | wx.RIGHT, 2)
        boxSizer.Add(self.widget, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(boxSizer)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self._bindWidgetEvent()
    # end _bindWidgetEvents()

    def _validateWidget(self):
        u"Called to validate the widget.  Subclasses should call this whenever their value has changed.  The event to do that will be subclass specific." #$NON-NLS-1$
        value = self._getWidgetValue()
        oldValid = self.isValid
        self.isValid = self.validator.isValid(value)
        if oldValid is not self.isValid:
            self._fireValidityEvent()
            self._setImageVisibility()
            self.Layout()

        # Always do this because the reason might change - which will not prompt a state transition, but
        # the image tooltip should change.
        if not self.isValid:
            self.warningImage.SetToolTipString(self.validator.getInvalidReason())
    # end _validateWidget()

    def _fireValidityEvent(self):
        event = None
        if self.isValid:
            event = ZWidgetValidEvent(self.GetId())
        else:
            event = ZWidgetInvalidEvent(self.GetId())

        self.GetEventHandler().AddPendingEvent(event)
    # end _fireValidityEvent()

    def _propagateEvent(self, event):
        newEvent = event.Clone()
        newEvent.SetId(self.GetId())
        self.GetEventHandler().AddPendingEvent(newEvent) 
    # end _propagateEvent()

    def _setImageVisibility(self):
        # Show the image only if the value is NOT valid.
        self.warningImage.Show(not self.isValid)
    # end _setImageVisibility()

    def _createWidget(self):
        u"Abstract method that should create the real wx widget whose value will be validated." #$NON-NLS-1$
    # end _createWidget()
    
    def _bindWidgetEvent(self):
        u"Called to bind the base widget's event to a callback.  Should be implemented by subclasses." #$NON-NLS-1$
    # end _bindWidgetEvent()
    
    def _getWidgetValue(self):
        u"Returns the value of the base widget.  Should be implemented by subclasses." #$NON-NLS-1$
    # end _getWidgetValue()

# end ZValidatingCtrl
