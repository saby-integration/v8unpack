from ..MetaDataObject.core.Simple import SimpleNameFolder
from ..MetaDataObject.versions.TaskForm803 import TaskForm803


class ChartOfAccountsForm(SimpleNameFolder):
    versions = {
        '803': TaskForm803
    }
