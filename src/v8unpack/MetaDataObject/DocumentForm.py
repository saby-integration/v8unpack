from ..MetaDataObject import MetaDataObject
from ..MetaDataObject.versions.DocumentForm803 import DocumentForm803


class DocumentForm(MetaDataObject):
    versions = {
        '803': DocumentForm803
    }
