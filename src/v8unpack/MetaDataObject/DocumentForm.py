from ..MetaDataObject.Form import Form
from ..MetaDataObject.versions.DocumentForm803 import DocumentForm803 as Form803
from ..MetaDataObject.versions.Form801 import Form801
from ..MetaDataObject.versions.Form802 import Form802
from ..MetaDataObject.versions.OldForm803 import OldForm801, OldForm802


class DocumentForm(Form):
    versions = {
        '801': Form801,
        '802': Form802,
        '803': Form803,
        '5-5': OldForm801,
        '7-7': OldForm801,
        '9-9': OldForm802,
        '0-5': Form801,
        '0-7': Form801,
        '0-9': Form802,
        '0-12': Form803,
        '0-13': Form803,
        '1-9': Form802,
        '1-12': Form803,
        '1-13': Form803
    }
