'''
Implementation of signal connecting strategy for ClutterScript.
'''
import sys

from gi.repository import GObject


"""
Object or module relative to which signal handlers are named
"""
BASE_NAMESPACE = sys.modules[__name__]


def resolve_name(handler_name):
    """
    Resolve python name to python value in current namespace
    """
    import pisak.handlers  # @UnusedImport
    name_parts = handler_name.split('.')
    current = BASE_NAMESPACE
    for part in name_parts:
        current = current.__dict__[part]
    return current


def resolve_handler(handler_name):
    """
    Resolve handler name and check for callability
    """
    function = resolve_name(handler_name)
    if callable(function):
        return function
    else:
        raise Exception("Specified handler is not a function")


def connect_function(gobject, signal, target, flags, function, data):
    # TODO:
    # make 'git grep connect' and redirect all the resulted connections in here
    if target is not None:
        if GObject.ConnectFlags.AFTER == flags:
            gobject.connect_object_after(signal, function, target, data)
        else:
            gobject.connect_object(signal, function, target, data)
    elif GObject.ConnectFlags.AFTER == flags:
        gobject.connect_after(signal, function, data)
    else:
        gobject.connect(signal, function, data)


def python_connect(script, gobject, signal, handler, target, flags):
    """
    Implementation of signal connector used by
    ClutterScript.connect_signals_full
    """
    function = resolve_handler(handler)
    connect_function(gobject, signal, target, flags, function)


_HANDLER_MAP = {}

def resolve_registered(handler):
    """
    Resolve registered function
    """
    function = _HANDLER_MAP.get(handler)
    if function is not None:
        return function
    else:
        raise Exception("No such function: " + handler)


def register_function(handler, function):
    """
    Registers a function as handler
    """
    if callable(function):
        _HANDLER_MAP[handler] = function
    else:
        raise Exception("Not a function", function)


def registered_handler(handler_name):
    """
    Decorator
    """
    def f_reg(function):
        register_function(handler_name, function)
        return function
    return f_reg


def connect_registered(script, gobject, signal, handler, target, flags, data):
    """
    Alternate implementation of signal connector. Uses only registered
    functions instead of introspection.
    """
    function = resolve_registered(handler)
    connect_function(gobject, signal, target, flags, function, data)
