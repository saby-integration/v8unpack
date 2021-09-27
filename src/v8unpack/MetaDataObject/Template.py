from ..MetaDataObject import MetaDataObject
from ..MetaDataObject.versions.Template83 import Template83
from ..MetaDataObject.versions.Template82 import Template82
from ..MetaDataObject.versions.Template81 import Template81


class Template(MetaDataObject):

    versions = {
        '81': Template81,
        '82': Template82,
        '83': Template83
    }
