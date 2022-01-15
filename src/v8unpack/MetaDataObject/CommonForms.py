from ..MetaDataObject.core.Simple import SimpleNameFolder
from ..MetaDataObject.versions.CommonForm803 import CommonForm803


class CommonForms(SimpleNameFolder):
    versions = {
        '803': CommonForm803
    }
