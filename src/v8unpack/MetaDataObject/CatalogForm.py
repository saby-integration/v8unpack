from ..MetaDataObject import MetaDataObject
from ..MetaDataObject.versions.DocumentForm83 import DocumentForm83


class CatalogForm(MetaDataObject):
    versions = {
        '83': DocumentForm83
    }
