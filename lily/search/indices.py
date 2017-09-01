from django.utils.encoding import python_2_unicode_compatible
from elasticsearch_dsl import Index as DSLIndex
from .registries import registry


@python_2_unicode_compatible
class Index(DSLIndex):
    def __init__(self, name, using='default'):
        super(Index, self).__init__(name, using)

    def doc_type(self, doc_type):
        """
        Extend to register the doc_type in the global document registry
        """
        doc_type = super(Index, self).doc_type(doc_type)
        registry.register(self, doc_type())
        return doc_type

    def __str__(self):
        return self._name

    # def create(self, **kwargs):
    #     """
    #     Creates the index in elasticsearch.
    #
    #     Any additional keyword arguments will be passed to
    #     ``Elasticsearch.indices.create`` unchanged.
    #     """
    #     index_name = '%s_%s' % (self._name, int(time()))
    #
    #     self.connection.indices.create(index=index_name, body=self.to_dict(), **kwargs)
    #     self.connection.indices.put_alias(index=index_name, name=self._name)
    #
    # def exists(self, **kwargs):
    #     """
    #     Returns ``True`` if the index already exists in elasticsearch.
    #
    #     Any additional keyword arguments will be passed to
    #     ``Elasticsearch.indices.exists`` unchanged.
    #     """
    #     return self.connection.indices.exists_alias(self.name)
    #
    # def delete(self, **kwargs):
    #     """
    #     Deletes the index in elasticsearch.
    #
    #     Any additional keyword arguments will be passed to
    #     ``Elasticsearch.indices.delete`` unchanged.
    #     """
    #     index_filter = '%s_*' % self._name
    #     alias = self.connection.indices.get_alias(index=index_filter, name=self._name, **kwargs)
    #
    #     import pdb; pdb.set_trace()
    #
    #     if len(alias) > 1:
    #         raise ElasticsearchError('Could not delete, multiple indexes exist for the alias %s' % self._name)
    #
    #     self.connection.indices.delete_alias(index=index_filter, name=self._name, **kwargs)
    #     return self.connection.indices.delete(index=alias.keys()[0], **kwargs)
