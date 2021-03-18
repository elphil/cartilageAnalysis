def set_trace():
    from PyQt5.QtCore import pyqtRemoveInputHook
    import pdb
    import sys
    pyqtRemoveInputHook()
    debugger = pdb.Pdb()
    debugger.reset()
    debugger.do_next(None)
    users_frame = sys._getframe().f_back
    debugger.set_trace(users_frame)

