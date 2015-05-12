import os

from pisak import __version_from_git
from pisak.libs import settings


"""
Absolute path to the package directory.
"""
PATH = os.path.abspath(os.path.split(__file__)[0])


version = __version_from_git.version()


"""
Global configuration object that contains all the default settings.
"""
config = settings.Config()


"""
Instance of the current application.
"""
app = None
