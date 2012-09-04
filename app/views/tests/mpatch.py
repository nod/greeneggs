from __future__ import with_statement
from types import ClassType, MethodType, TypeType


class ArgCapt(object):

    def __init__(self, m):
        self.m = m
        self.argcapts = []

    def __call__(self, *a, **kw):
        print "ARGCAPT", a, kw
        self.argcapts.append(dict(a=a, kw=kw))
        return self.m(*a, **kw)


class Patch(object):

    class Missing:
        pass

    def __init__(self, tgt, **kwargs):
        self.target = tgt
        self._patches = kwargs
        self.memos = dict()

    def __enter__(self):
        self._saved = {}
        for name, method in self._patches.iteritems():
            self._saved[name] = self.target.__dict__.get(name, self.Missing)
            setattr(self.target, name, self._rebind_method(method))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for name, method in self._saved.iteritems():
            if method is not self.Missing:
                setattr(self.target, name, method)
            else:
                delattr(self.target, name)

    def _rebind_method(self, method):
        if not method:
            method = self._get_noop_method()
        if isinstance(method, MethodType):
            method = self._get_unbound_method(method)
        if not isinstance(self.target, (ClassType, TypeType)):
            method = self._bind_method_to_instance(method)
        return method

    def _get_noop_method(self):
        return lambda *args, **kwargs: None

    def _get_unbound_method(self, method):
        return method.im_func

    def _bind_method_to_instance(self, method):
        return method.__get__(self.target, type(self.target))


class CapturePatch(Patch):

    def __enter__(self):
        self._saved = {}
        for name, method in self._patches.iteritems():
            self._saved[name] = self.target.__dict__.get(name, self.Missing)
            print self.target.render
            setattr(self.target, name, ArgCapt(self._rebind_method(method)))
            print self.target.render

        return self


