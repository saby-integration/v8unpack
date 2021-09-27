from ..MetaDataObject import MetaDataObject
from ..MetaDataObject.versions.Form83 import Form83
from ..MetaDataObject.versions.Form82 import Form82
from ..MetaDataObject.versions.Form81 import Form81


class Form(MetaDataObject):
    versions = {
        '81': Form81,
        '82': Form82,
        '83': Form83
    }
