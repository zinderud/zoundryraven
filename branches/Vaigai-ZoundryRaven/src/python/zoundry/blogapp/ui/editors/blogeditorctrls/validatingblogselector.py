from zoundry.appframework.ui.widgets.controls.validating.standard.combobox import ZValidatingComboBox
from zoundry.blogapp.ui.editors.blogeditorctrls.blogselector import ZBlogSelectorCombo
from zoundry.blogapp.ui.events.editors.blogeditorevents import ZEVT_BLOG_SELECTOR_COMBO
import wx

# ------------------------------------------------------------------------------
# A validating blog selector combo.
# ------------------------------------------------------------------------------
class ZValidatingBlogSelectorCombo(ZValidatingComboBox):

    def __init__(self, validator, model, parent, id = wx.ID_ANY, value = u"", size = wx.DefaultSize, style = 0): #$NON-NLS-1$
        self.model = model

        ZValidatingComboBox.__init__(self, validator, parent, id, value, size, style)
    # end __init__()

    def _createWidget(self):
        return ZBlogSelectorCombo(self, self.model)
    # end _createWidget()

    def _bindWidgetEvent(self):
        self.Bind(ZEVT_BLOG_SELECTOR_COMBO, self.onEvent, self.widget)
    # end _bindWidgetEvent()

    # Redefine some methods that are exposed by the widget being validated

    def getBlog(self):
        return self.widget.getBlog()
    # end getBlog()

    def selectBlog(self, accountId, blogId):
        self.widget.selectBlog(accountId, blogId)
    # end selectBlog()

# end ZValidatingBlogSelectorCombo
