from ..MetaDataObject.core.Simple import SimpleNameFolder
from ..MetaDataObject.versions.ReportForm803 import ReportForm803


class ReportForm(SimpleNameFolder):
    versions = {
        '803': ReportForm803
    }
