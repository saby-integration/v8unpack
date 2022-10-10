from ..MetaDataObject.core.Simple import SimpleNameFolder
from ..MetaDataObject.versions.Form803 import Form803


class ReportForm(SimpleNameFolder):
    versions = {
        '803': Form803
    }
