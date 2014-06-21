from zoundry.base.net.http import ZSimpleHTTPRequest
from zoundry.base.net.authhandlers import ZAuthHandler

#-------------------------------------------------------------
# Google GData related code
#-------------------------------------------------------------


#-------------------------------------------------------------
# Google gdata login handler
#-------------------------------------------------------------
class ZGoogleLoginAuthHandler(ZAuthHandler):
    SCHEME = u"googlelogin" #$NON-NLS-1$
    def __init__(self):
        ZAuthHandler.__init__(self, ZGoogleLoginAuthHandler.SCHEME)

    def supported(self, httpResp):
        wwwauth = self._getWWWAuthenticate(httpResp)
        return wwwauth.lower().startswith(u"googlelogin ") #$NON-NLS-1$

    def handleRequest(self, httpResp, url, username, password): #@UnusedVariable
        rVal = {}        
        serviceName = ZGDataLogin.BLOGGGER_GDATA_SERVICE
        # hack to check to see if Picasa login service is required (based on uri path).
        if url and url.find(u"/data/feed/api/user") != -1: #$NON-NLS-1$
            serviceName = ZGDataLogin.PICASA_GDATA_SERVICE
        self._debug(u"Using GoogleLogin service %s for user %s" % (serviceName, username) ) #$NON-NLS-1$
        glogin = ZGDataLogin(username, password, serviceName)
        glogin.setLogger(self.logger)
        if glogin.login():
            auth = u"GoogleLogin auth=%s" % glogin.getAuth() #$NON-NLS-1$
            rVal[u"Authorization"] = auth #$NON-NLS-1$
        else:
            self._debug(u"GoogleLogin failed for user %s" % username ) #$NON-NLS-1$
            self._debug(u"GoogleLogin error: %s" % glogin.getGDataErrorMessage() ) #$NON-NLS-1$
            if glogin.isCaptchaRequired():
                self._debug(u"GoogleLogin captcha image url: %s" % glogin.getCaptchaImageUrl() ) #$NON-NLS-1$
        return rVal

class ZGDataLogin:
    
    BLOGGGER_GDATA_SERVICE  = u"blogger" #$NON-NLS-1$
    PICASA_GDATA_SERVICE  = u"lh2" #$NON-NLS-1$
    
    IMAGE_BASE_URL = u"http://www.google.com/accounts/" #$NON-NLS-1$
    LOGIN_ENDPOINT = u"https://www.google.com/accounts/ClientLogin" #$NON-NLS-1$
    SOURCE         = u"Zoundry-Raven-2.0"  #$NON-NLS-1$

    GDATA_MESSAGES = {}
    GDATA_MESSAGES [u"badauthentication"] = u"BadAuthentication: The login request used a username or password that is not recognized." #$NON-NLS-1$ #$NON-NLS-2$
    GDATA_MESSAGES [u"notverified"] = u"NotVerified: The account email address has not been verified. The user will need to access their Google account directly to resolve the issue before logging in using a non-Google application." #$NON-NLS-1$ #$NON-NLS-2$
    GDATA_MESSAGES [u"termsnotagreed"] = u"TermsNotAgreed: The user has not agreed to terms. The user will need to access their Google account directly to resolve the issue before logging in using a non-Google application." #$NON-NLS-1$ #$NON-NLS-2$
    GDATA_MESSAGES [u"captcharequired"] = u"CaptchaRequired: A CAPTCHA is required." #$NON-NLS-1$ #$NON-NLS-2$
    GDATA_MESSAGES [u"unknown"] = u"Unknown: The error is unknown or unspecified; the request contained invalid input or was malformed." #$NON-NLS-1$ #$NON-NLS-2$
    GDATA_MESSAGES [u"accountdeleted"] = u"AccountDeleted: The user account has been deleted." #$NON-NLS-1$ #$NON-NLS-2$
    GDATA_MESSAGES [u"accountdisabled"] = u"AccountDisabled: The user account has been disabled." #$NON-NLS-1$ #$NON-NLS-2$
    GDATA_MESSAGES [u"serviceunavailable"] = u"ServiceUnavailable: The service is not available; try again later." #$NON-NLS-1$ #$NON-NLS-2$

    def __init__(self, username, password, serviceName):
        self.username = username
        self.password = password
        self.serviceName = serviceName
        self.connected = False
        self.ok = False
        self.httpCode = 0
        self.httpMessage = u"" #$NON-NLS-1$
        self.gdataError = None
        self.captchaToken = None
        self.captchaUrl = None
        self.loginCaptcha = None
        # gdata auth cookies
        self.sid = None
        self.lsid = None
        self.auth = None
        self.logger = None

    def setLogger(self, logger):
        self.logger = logger
        
    def _debug(self, s):
        if self.logger:
            msg = u"GDataLogin: %s" % s #$NON-NLS-1$
            self.logger.debug(msg)

    def _reset(self):
        self.connected = False
        self.ok = False
        self.httpCode = 0
        self.httpMessage = u"" #$NON-NLS-1$
        self.gdataError = None
        self.sid = None
        self.lsid = None
        self.auth = None

    def login(self, captchaText=None):
        if captchaText and len(captchaText.strip()) > 0:
            self.setLoginCaptcha(captchaText.strip())
        self._reset()
        self._connect()
        return self.isOk()

    def isOk(self):
        self._connect()
        return self.ok

    def getAuth(self):
        self._connect()
        return self.auth

    def getSid(self):
        self._connect()
        return self.sid

    def getLsid(self):
        self._connect()
        return self.lsid

    def isCaptchaRequired(self):
        self._connect()
        rVal = False
        return rVal

    def getCaptchaImageUrl(self):
        self._connect()
        return self.captchaUrl

    def getHttpCode(self):
        self._connect()
        return self.httpCode

    def getGDataError(self):
        self._connect()
        return self.gdataError

    def getGDataErrorMessage(self):
        rVal = u"GData error message not available"  #$NON-NLS-1$
        code = self.getGDataError()
        if code:
            key = code.strip().lower()
            if ZGDataLogin.GDATA_MESSAGES.has_key(key):
                rVal = ZGDataLogin.GDATA_MESSAGES[key]
            elif len(key) > 0:
                rVal = code
        return rVal

    def getLoginCaptcha(self):
        return self.loginCaptcha

    def setLoginCaptcha(self, captchaText):
        self.loginCaptcha = captchaText

    def _connect(self):
        if self.connected:
            return
        self._reset()
        self._debug(u"Sending GoogleLogin request for service=%s, user= %s to endpoint %s" %(self.serviceName, self.username, ZGDataLogin.LOGIN_ENDPOINT)) #$NON-NLS-1$
        params = {}
        params[u"Email"] = self.username  #$NON-NLS-1$
        params[u"Passwd"] = self.password  #$NON-NLS-1$
        params[u"service"] = self.serviceName  #$NON-NLS-1$
        params[u"source"] = ZGDataLogin.SOURCE  #$NON-NLS-1$
        if self.captchaToken and self.loginCaptcha:
            params[u"logintoken"] = self.captchaToken  #$NON-NLS-1$
            params[u"logincaptcha"] = self.loginCaptcha  #$NON-NLS-1$
            self._debug(u"Sending GoogleLogin logintoken: %s" %self.captchaToken) #$NON-NLS-1$
            self._debug(u"Sending GoogleLogin logincaptcha: %s" %self.loginCaptcha) #$NON-NLS-1$
        conn = ZSimpleHTTPRequest(ZGDataLogin.LOGIN_ENDPOINT)  #$NON-NLS-1$
        self.connected = True
        conn.send(params)
        self.httpCode = conn.getHttpStatusCode()
        self.httpMessage = conn.getHttpStatusMessage()
        self._debug(u"GoogleLogin response code: %d, %s" % (self.httpCode, self.httpMessage)) #$NON-NLS-1$
        self.ok = self.httpCode == 200
        if self.httpCode == 200 or self.httpCode == 403:
            data = conn.getResponse()
            self._parseData(data)

    def _parseData(self,data):
        if not data:
            return
        sep = u"\n"  #$NON-NLS-1$
        if data.find(u"\r\n") != -1: #$NON-NLS-1$
            sep = u"\r\n" #$NON-NLS-1$
        elif data.find(u"\r") != -1: #$NON-NLS-1$
            sep = u"\r" #$NON-NLS-1$
        # reset captch
        self.captchaUrl = None
        self.captchaToken = None
        lines = data.strip().split(sep)
        nvmap = {}
        for line in lines:
            idx = line.find(u"=") #$NON-NLS-1$
            if idx == -1:
                continue
            name = line[0:idx]
            value = line[idx+1:]
            name = name.strip().lower()
            value = value.strip()
            nvmap[name] = value
            self._debug(u"GoogleLogin response data: %s=%s" % (name, value)) #$NON-NLS-1$
        if nvmap.has_key(u"sid"): #$NON-NLS-1$
            self.sid = nvmap[u"sid"] #$NON-NLS-1$
        if nvmap.has_key(u"lsid"): #$NON-NLS-1$
            self.lsid = nvmap[u"lsid"] #$NON-NLS-1$
        if nvmap.has_key(u"auth"): #$NON-NLS-1$
            self.auth = nvmap[u"auth"] #$NON-NLS-1$
        if nvmap.has_key(u"error"): #$NON-NLS-1$
            self.gdataError = nvmap[u"error"] #$NON-NLS-1$
        if nvmap.has_key(u"captchatoken"): #$NON-NLS-1$
            self.captchaToken = nvmap[u"captchatoken"] #$NON-NLS-1$
        if nvmap.has_key(u"captchaurl"): #$NON-NLS-1$
            self.captchaUrl = nvmap[u"captchaurl"] #$NON-NLS-1$

        if self.captchaUrl and not self.captchaUrl.startswith(u"http"): #$NON-NLS-1$
            # handle relative urls
            self.captchaUrl = ZGDataLogin.IMAGE_BASE_URL.rstrip(u"/") + self.captchaUrl.lstrip(u"/") #$NON-NLS-1$  #$NON-NLS-2$
