#!/usr/bin/env python
'''
Taken from https://gist.github.com/tito/5844528
Run a python method into Activity thread
========================================
Python decorator for running a python method into the Activity ui thread.
This is a way to resolve thoses kind of errors:
- java.lang.RuntimeException: Can't create handler inside thread that has not called Looper.prepare()
- NullPointerException in enableForegroundDispatch due to ActivityThread.currentActivityThread() return null
How to use it::
    @run_on_ui_thread
    def nfc_enable_ndef_exchange(self):
        self.nfc_adapter.enableForegroundNdefPush(self.j_context, ndef_message)
        self.nfc_adapter.enableForegroundDispatch(self.j_context,
                self.nfc_pending_intent, self.ndef_exchange_filters, None)
'''

from jnius import autoclass, PythonJavaClass, java_method

PythonActivity = autoclass('org.renpy.android.PythonActivity')


class Runnable(PythonJavaClass):
    __javainterfaces__ = ['java/lang/Runnable']
    __runnables__ = []

    def __init__(self, func):
        super(Runnable, self).__init__()
        self.func = func

    def __call__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs
        PythonActivity.mActivity.runOnUiThread(self)
        Runnable.__runnables__.append(self)

    @java_method('()V')
    def run(self):
        try:
            ret = self.func(*self.args, **self.kwargs)
            if self.callback:
                self.callback(ret)
        except:
            import trackback
            trackback.print_exc()

        Runnable.__runnables__.remove(self)

def run_on_ui_thread(f):
    def f2(*args, **kwargs):
        Runnable(f)(args, kwargs)
    return f2
