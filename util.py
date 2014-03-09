import sys
import os.path
import sublime_plugin
import sublime
import threading


def update_sys_path():
    plugin_dir = os.path.dirname(__file__)
    lib_dir = os.path.join(os.path.dirname(__file__), "lib")
    server_dir = os.path.join(os.path.dirname(__file__), "server")
    path_extensions = [plugin_dir, lib_dir, server_dir]

    for pe in path_extensions:
        if pe not in sys.path:
            sys.path.insert(0, pe)


class SimpleClearAndInsertCommand(sublime_plugin.TextCommand):
    '''utility command class for writing into the documentation view'''
    def run(self, edit, block=False, **kwargs):
        doc = kwargs['insert_string']
        r = sublime.Region(0, self.view.size())
        self.view.erase(edit, r)
        self.view.insert(edit, 0, doc)


class AsynchronousFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.

    Used for reading stderr output of the server.
    '''

    def __init__(self, name, fd, queue):
        threading.Thread.__init__(self)
        self.name = name
        self._fd = fd
        self._queue = queue

    def run(self):
        '''The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            if line:
                self._queue.put("{0}: {1}".format(self.name, line))


class DebugProcDummy(object):
    """Used only for debugging, when the server process is started externally
    """
    def poll(*args):
        return None

    def terminate():
        pass

