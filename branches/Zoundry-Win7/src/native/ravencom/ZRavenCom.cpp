// ZRavenCom.cpp

#include "Python.h"
#include "PyWinTypes.h"

#include "PyICustomDoc.h"
#include "PyIDocHostUIHandler.h"
#include "PythonCOMRegister.h"

#include "ZRavenMisc.h"

#include "WinInet.h"
#define MAX_CACHE_ENTRY_INFO_SIZE 4096

// NOTE: 1) It doesn't appear that the pattern argument is useful for targetting a particular file.
//		 2) For some reason, even though we allocate a 4K buffer, we are still getting
//		    ERROR_INSUFFICIENT_BUFFER errors and the buffer sizes that are insufficient are smaller.
bool internalGetCachedIEUrl(char* filepath, /*in out*/char** url)
{
	bool ret = false;
	INTERNET_CACHE_ENTRY_INFO* picei = (INTERNET_CACHE_ENTRY_INFO* )new TCHAR[MAX_CACHE_ENTRY_INFO_SIZE];
	DWORD infoBufferSize = MAX_CACHE_ENTRY_INFO_SIZE;
	picei->dwStructSize = infoBufferSize;
	HANDLE h = FindFirstUrlCacheEntry(NULL, picei, &infoBufferSize);
	if (h == NULL) {
		DWORD error = GetLastError();
		if (error == ERROR_INSUFFICIENT_BUFFER) {
			delete picei; picei = NULL;
			picei = (INTERNET_CACHE_ENTRY_INFO* )new TCHAR[infoBufferSize];
			picei->dwStructSize = infoBufferSize;
			h = FindFirstUrlCacheEntry(NULL, picei, &infoBufferSize);
		}
	}
	if (h != NULL) {
		while(true) {
			if (picei->lpszLocalFileName != NULL) {
				if (_tcscmp(filepath, picei->lpszLocalFileName) == 0) {
					if (picei->lpszSourceUrlName != NULL) {
						strcpy(*url, picei->lpszSourceUrlName);
						ret = true;
						break;
					}
				}
			}
			if (!FindNextUrlCacheEntry(h, picei, &infoBufferSize)) {
				DWORD error = GetLastError();
				if (error == ERROR_INSUFFICIENT_BUFFER) {
					delete picei; picei = NULL;
					picei = (INTERNET_CACHE_ENTRY_INFO* )new TCHAR[infoBufferSize];
					picei->dwStructSize = infoBufferSize;
					if (!FindNextUrlCacheEntry(h, picei, &infoBufferSize)) {
						break;
					}
				} else {	// end or error
					break;
				}
			}
		}
		FindCloseUrlCache(h);
	}
	delete picei;
	return ret;
}

PyObject *getCachedIEUrl(PyObject * self, PyObject *args)
{
	// Get Python Arguments
	TCHAR* filepath = NULL;
	if (!PyArg_ParseTuple(args, "s", &filepath)) {
		return NULL;
	}

	TCHAR* url = new TCHAR[8192]; *url = '\0';
	bool ret = internalGetCachedIEUrl(filepath, &url);
	PyObject * pyurl = NULL;
	pyurl = Py_BuildValue("s", url);
	delete url;
	return pyurl;
}

// ------------------- Module Stuff -------------------------------
static struct PyMethodDef zravencom_methods[]=
{
	{"getCachedIEUrl", getCachedIEUrl, METH_VARARGS},
	{"SetMSHTMLCaretPosition", SetMSHTMLCaretPosition, METH_VARARGS},
	{ NULL }
};

static const PyCom_InterfaceSupportInfo register_data[] =
{
	PYCOM_INTERFACE_CLIENT_ONLY ( CustomDoc ),
	PYCOM_INTERFACE_SERVER_ONLY ( DocHostUIHandler ),
};

extern "C" __declspec(dllexport)
void initzravencom(void)
{

	// Initialize PyWin32 globals (such as error objects etc)
	PyWinGlobals_Ensure();

	PyObject *module = Py_InitModule("zravencom", zravencom_methods);
	if (module==NULL)
		return;

	PyObject *dict = PyModule_GetDict(module);
	if (dict==NULL)
		return;

	// Register all of our interfaces, gateways and IIDs.
	PyCom_RegisterExtensionSupport(dict, register_data, sizeof(register_data)/sizeof(PyCom_InterfaceSupportInfo));
}
