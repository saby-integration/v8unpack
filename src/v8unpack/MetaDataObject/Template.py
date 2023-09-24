from ..MetaDataObject import MetaDataObject
from ..MetaDataObject.versions.Template801 import Template801
from ..MetaDataObject.versions.Template802 import Template802
from ..MetaDataObject.versions.Template803 import Template803


class Template(MetaDataObject):
    versions = {
        '801': Template801,
        '802': Template802,
        '803': Template803
    }
