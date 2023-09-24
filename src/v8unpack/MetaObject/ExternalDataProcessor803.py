from .ExternalDataProcessor import ExternalDataProcessor


class ExternalDataProcessor803(ExternalDataProcessor):
    def encode_version(self):
        return self.data['version']
