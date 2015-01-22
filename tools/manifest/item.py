from abc import ABCMeta, abstractmethod, abstractproperty

from utils import url_to_rel_path

class ManifestItem(object):
    __metaclass__ = ABCMeta

    item_type = None

    def __init__(self):
        self.manifest = None

    @abstractmethod
    def key(self):
        pass

    def __eq__(self, other):
        if not hasattr(other, "key"):
            return False
        return self.key() == other.key()

    def __hash__(self):
        return hash(self.key())

    @abstractmethod
    def to_json(self):
        raise NotImplementedError

    @classmethod
    def from_json(self, manifest, obj):
        raise NotImplementedError

    @abstractproperty
    def id(self):
        pass


class URLManifestItem(ManifestItem):
    def __init__(self, url, url_base="/"):
        ManifestItem.__init__(self)
        self.url = url
        self.url_base = url_base

    @property
    def id(self):
        return self.url

    def key(self):
        return self.item_type, self.url

    @property
    def path(self):
        return url_to_rel_path(self.url, self.url_base)

    def to_json(self):
        rv = {"url": self.url}
        return rv

    @classmethod
    def from_json(cls, manifest, obj):
        return cls(obj["url"],
                   url_base=manifest.url_base)


class TestharnessTest(URLManifestItem):
    item_type = "testharness"

    def __init__(self, url, url_base="/", timeout=None):
        URLManifestItem.__init__(self, url, url_base=url_base)
        self.timeout = timeout

    def to_json(self):
        rv = {"url": self.url}
        if self.timeout is not None:
            rv["timeout"] = self.timeout
        return rv

    @classmethod
    def from_json(cls, manifest, obj):
        return cls(obj["url"],
                   url_base=manifest.url_base,
                   timeout=obj.get("timeout"))


class RefTest(URLManifestItem):
    item_type = "reftest"

    def __init__(self, url, references, url_base="/", timeout=None, is_reference=False):
        URLManifestItem.__init__(self, url, url_base=url_base)
        for _, ref_type in references:
            if ref_type not in ["==", "!="]:
                raise ValueError, "Unrecognised ref_type %s" % ref_type
        self.references = tuple(references)
        self.timeout = timeout
        self.is_reference = is_reference

    @property
    def id(self):
        return self.url

    def key(self):
        return self.item_type, self.url

    def to_json(self):
        rv = {"url": self.url,
              "references": self.references}
        if self.timeout is not None:
            rv["timeout"] = self.timeout
        return rv

    @classmethod
    def from_json(cls, manifest, obj):
        return cls(obj["url"],
                   obj["references"],
                   url_base=manifest.url_base,
                   timeout=obj.get("timeout"))


class ManualTest(URLManifestItem):
    item_type = "manual"

class Stub(URLManifestItem):
    item_type = "stub"

class WebdriverSpecTest(ManifestItem):
    item_type = "wdspec"

    def __init__(self, path):
        ManifestItem.__init__(self)
        self.path = path

    @property
    def id(self):
        return self.path

    def to_json(self):
        return {"path": self.path}

    def key(self):
        return self.path

    @classmethod
    def from_json(cls, manifest, obj):
        return cls(path=obj["path"])
