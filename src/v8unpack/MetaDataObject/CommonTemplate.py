from ..MetaDataObject import MetaDataObject
from ..MetaDataObject.versions.CommonTemplate803 import CommonTemplate803
from ..MetaDataObject.versions.CommonTemplate802 import CommonTemplate802


class CommonTemplate(MetaDataObject):
    versions = {
        '802': CommonTemplate802,
        '803': CommonTemplate803,
        4: CommonTemplate803
    }
