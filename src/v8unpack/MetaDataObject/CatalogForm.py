from ..MetaDataObject.core.Simple import Simple
from ..MetaDataObject.versions.DocumentForm803 import DocumentForm803


class CatalogForm(Simple):
    versions = {
        '803': DocumentForm803
    }
