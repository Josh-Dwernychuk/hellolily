class ElasticsearchError(Exception):
    pass


class VariableLookupError(ElasticsearchError):
    pass


class ModelFieldNotMappedError(ElasticsearchError):
    pass
