from zoundry.blogapp.messages import _extstr

#----------------------------------
# Common menu labels shared by menus and image properties dialog
#----------------------------------
class ZImageBorderMenuLabels:
    NONE   = u"none"  #$NON-NLS-1$
    SOLID  = u"solid"  #$NON-NLS-1$
    DASHED = u"dashed"  #$NON-NLS-1$
    DOTTED = u"dotted"  #$NON-NLS-1$
    DOUBLE = u"double"  #$NON-NLS-1$
    GROOVE = u"groove"  #$NON-NLS-1$
    INSERT = u"inset"  #$NON-NLS-1$
    OUTSET = u"outset"  #$NON-NLS-1$
    RIDGE  = u"ridge"  #$NON-NLS-1$
        
    BORDER_KEYWORDS = [NONE, SOLID, DASHED, DOTTED, DOUBLE, GROOVE, INSERT, OUTSET, RIDGE]
    BORDER_LABELS = {NONE   : _extstr(u"blogcontenteditorimagebordermenumodel.BorderNone"),  #$NON-NLS-1$
                     SOLID  : _extstr(u"blogcontenteditorimagebordermenumodel.BorderSolid"),  #$NON-NLS-1$
                     DASHED : _extstr(u"blogcontenteditorimagebordermenumodel.BorderDashed"),  #$NON-NLS-1$
                     DOTTED : _extstr(u"blogcontenteditorimagebordermenumodel.BorderDotted"),  #$NON-NLS-1$
                     DOUBLE : _extstr(u"blogcontenteditorimagebordermenumodel.BorderDouble"),  #$NON-NLS-1$
                     GROOVE : _extstr(u"blogcontenteditorimagebordermenumodel.BorderGroove"),  #$NON-NLS-1$
                     INSERT : _extstr(u"blogcontenteditorimagebordermenumodel.BorderInset"),  #$NON-NLS-1$
                     OUTSET : _extstr(u"blogcontenteditorimagebordermenumodel.BorderOutset"),  #$NON-NLS-1$
                     RIDGE  : _extstr(u"blogcontenteditorimagebordermenumodel.BorderRidge")  #$NON-NLS-1$
                     }

# end


#----------------------------------
# Common menu labels.
#----------------------------------
class ZImageAlignMenuLabels:
    NONE   = u"none"  #$NON-NLS-1$
    LEFT   = u"left"  #$NON-NLS-1$
    CENTER = u"center"  #$NON-NLS-1$
    RIGHT  = u"right"  #$NON-NLS-1$
        
    ALIGN_KEYWORDS = [NONE, LEFT, CENTER, RIGHT]
    ALIGN_LABELS = {NONE   : _extstr(u"blogcontenteditorimagealignmenumodel.AlignNone"),  #$NON-NLS-1$
                     LEFT  : _extstr(u"blogcontenteditorimagealignmenumodel.AlignLeft"),  #$NON-NLS-1$
                     CENTER : _extstr(u"blogcontenteditorimagealignmenumodel.AlignCenter"),  #$NON-NLS-1$
                     RIGHT : _extstr(u"blogcontenteditorimagealignmenumodel.AlignRight") #$NON-NLS-1$
                     }

# end

#----------------------------------
# Common menu labels shared by menus and image properties dialog
#----------------------------------
class ZThumbnailSizeMenuLabels:
    _75  = 75
    _100 = 100
    _250 = 250
    _400 = 400
    _500 = 500
    _600 = 600
    _800 = 800
        
    SIZE_KEYWORDS = [_75, _100, _250, _400, _500, _600, _800]
    SIZE_LABELS = {_75    : u"75px X 75px", #$NON-NLS-1$
                     _100   : u"100px X 100px", #$NON-NLS-1$
                     _250   : u"250px X 250px", #$NON-NLS-1$
                     _400   : u"400px X 400px", #$NON-NLS-1$
                     _500   : u"500px X 500px", #$NON-NLS-1$
                     _600   : u"600px X 600px", #$NON-NLS-1$
                     _800   : u"800px X 800px", #$NON-NLS-1$
                     }

# end
