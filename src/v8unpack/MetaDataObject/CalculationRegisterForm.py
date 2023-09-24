from ..MetaDataObject.core.Simple import SimpleNameFolder
from ..MetaDataObject.versions.DocumentForm803 import DocumentForm803


class CalculationRegisterForm(SimpleNameFolder):
    versions = {
        '803': DocumentForm803
    }
