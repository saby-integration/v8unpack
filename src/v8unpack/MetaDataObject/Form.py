from ..MetaDataObject.core.Simple import SimpleNameFolder
from ..MetaDataObject.versions.Form801 import Form801
from ..MetaDataObject.versions.Form802 import Form802
from ..MetaDataObject.versions.Form803 import Form803


class Form(SimpleNameFolder):
    versions = {
        '801': Form801,
        '802': Form802,
        '803': Form803
    }
