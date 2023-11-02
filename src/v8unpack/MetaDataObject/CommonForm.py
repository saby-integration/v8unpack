from ..MetaDataObject.core.Simple import SimpleNameFolder
from ..MetaDataObject.versions.CommonForm803 import CommonForm803


class CommonForm(SimpleNameFolder):
    versions = {
        '802': CommonForm803,
        '803': CommonForm803,
        4: CommonForm803
    }
