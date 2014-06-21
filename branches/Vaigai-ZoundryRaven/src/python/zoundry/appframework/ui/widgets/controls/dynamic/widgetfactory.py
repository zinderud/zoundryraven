from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingPasswordCtrl
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZNullControlValidator
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZRegexpControlValidator
import wx

# ----------------------------------------------------------------------------------------
# This class is used to create widgets dynmically based on a set of properties.
#
# The main entry point into the factory is the "createWidget" method.  This method will
# take a map of properties and return a newly created widget.  If anything goes wrong,
# an exception will be thrown.  The following properties are found in the map:
#
# Properties:
#   type : The widget type (text, password, checkbox) [defaults to 'text' if missing]
#   name : The name of the widget  [default is type dependant]
#   value : The initial value of the widget  [default is type dependant]
#   label : The widget's label (used for checkbox, for example)   [default is '']
#   tooltip : The widget's tooltip  [default is '']
#   validation-regexp : A regular expression used for validation  [no validation is done if missing]
#   validation-error-message : The error message shown when validation fails
# ----------------------------------------------------------------------------------------
class ZWidgetFactory:

    def __init__(self, parent, bindToParent = False):
        self.parent = parent
        self.bindToParent = bindToParent
    # end __init__()

    def createWidget(self, properties):
        type = self._getProperty(properties, u"type", u"text") #$NON-NLS-1$ #$NON-NLS-2$
        if type == u"text": #$NON-NLS-1$
            return self._createTextCtrl(properties)
        elif type == u"password": #$NON-NLS-1$
            return self._createPasswordCtrl(properties)
        elif type == u"checkbox": #$NON-NLS-1$
            return self._createCheckboxCtrl(properties)
    # end createWidget()

    def _createTextCtrl(self, properties):
        return self._createStandardControl(properties, ZValidatingTextCtrl, self.bindToParent)
    # end _createTextCtrl()

    def _createPasswordCtrl(self, properties):
        return self._createStandardControl(properties, ZValidatingPasswordCtrl, self.bindToParent)
    # end _createPasswordCtrl()

    def _createCheckboxCtrl(self, properties):
        name = self._getProperty(properties, u"name", u"ZDynamicCheckboxCtrl") #$NON-NLS-2$ #$NON-NLS-1$
        value = self._getProperty(properties, u"value", u"") #$NON-NLS-2$ #$NON-NLS-1$
        label = self._getProperty(properties, u"label", u"") #$NON-NLS-2$ #$NON-NLS-1$
        tooltip = self._getProperty(properties, u"tooltip", u"") #$NON-NLS-1$ #$NON-NLS-2$

        checkbox = wx.CheckBox(self.parent, wx.ID_ANY, label, name = name)
        if value == u"true" or value == u"True": #$NON-NLS-1$ #$NON-NLS-2$
            checkbox.SetValue(True)
        checkbox.SetToolTipString(tooltip)
        return checkbox
    # end _createCheckboxCtrl()

    def _createStandardControl(self, properties, controlClass, bindToParent = False):
        name = self._getProperty(properties, u"name", u"ZDynamicCtrl") #$NON-NLS-2$ #$NON-NLS-1$
        value = self._getProperty(properties, u"value", u"") #$NON-NLS-2$ #$NON-NLS-1$
        tooltip = self._getProperty(properties, u"tooltip", u"") #$NON-NLS-1$ #$NON-NLS-2$
        valRegexp = self._getProperty(properties, u"validation-regexp") #$NON-NLS-1$
        valErrorMessage = self._getProperty(properties, u"validation-error-message") #$NON-NLS-1$

        validator = ZNullControlValidator()
        if valRegexp:
            validator = ZRegexpControlValidator(valRegexp, valErrorMessage)

        control = controlClass(validator, self.parent, value = value, name = name)
        control.SetToolTipString(tooltip)
        if bindToParent:
            self.parent._bindValidatingWidget(control)
        return control
    # end _createTextCtrl()
    
    def _getProperty(self, properties, key, dflt = None):
        if key in properties:
            value = properties[key]
            if value:
                return value
        return dflt
    # end _getProperty()

# end ZWidgetFactory
