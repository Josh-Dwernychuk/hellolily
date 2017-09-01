class ElasticsearchError(Exception):
    pass


class VariableLookupError(ElasticsearchError):
    pass


class RedeclaredFieldError(ElasticsearchError):
    pass


class ModelFieldNotMappedError(ElasticsearchError):
    pass
