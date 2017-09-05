from django.db import models
from django.db.models.query_utils import Q
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Bool, Term, Range, Terms, Prefix, Exists, Regexp
import six

from lily.search.registries import registry
from lily.tenant.middleware import get_current_user


class ElasticQuerySet(models.QuerySet):
    """
    Override the default QuerySet with Elasticsearch capabilities.
    """

    def __init__(self, model=None, query=None, using=None, hints=None, search=None):
        super(ElasticQuerySet, self).__init__(model=model, query=query, using=using, hints=hints)
        if search is None:
            doc_types = registry.get_documents([model])

            search = Search(
                index=[doc_type.meta.index for doc_type in doc_types],
                doc_type=list(doc_types)
            )[0:10000]
        self.search = search
        self._total = None

    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results.
        """
        if not isinstance(k, (slice,) + six.integer_types):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0)) or
                (isinstance(k, slice) and (k.start is None or k.start >= 0) and
                 (k.stop is None or k.stop >= 0))), \
            "Negative indexing is not supported."

        if self._result_cache is not None:
            return self._result_cache[k]

        if isinstance(k, slice):
            qs = self._clone()
            if k.start is not None:
                start = int(k.start)
            else:
                start = 0
            if k.stop is not None:
                stop = int(k.stop)
            else:
                stop = start + 10000
            qs.search = qs.search[start:stop]
            return qs
        else:
            qs = self._clone()
            qs.search = qs.search[k:k+1]
            return list(qs)[0]

    def _sql_iterator(self):
        """
        Use the base QuerySet iterator() method to get results from the DB.

        Returns:
            iter: An iterator over the database results.
        """
        return super(ElasticQuerySet, self).iterator()

    def _fetch_all(self):
        """
        Fetch all models from the database based on the Elasticsearch results.

        Populates self._result_cache with a list of models from the
        Elasticsearch results.
        """
        if self._result_cache is None:
            response = self.search.execute(ignore_cache=True)
            self._total = response.hits.total
            ids = [hit.meta.id for hit in response.hits]

            obj = self._clone()
            obj.query.add_q(Q(pk__in=ids))
            models = {obj._get_pk_val(): obj for obj in obj._sql_iterator()}

            sorted_models = []
            for idx in ids:
                if int(idx) in models:
                    sorted_models.append(models[int(idx)])
            self._result_cache = sorted_models

        if self._prefetch_related_lookups and not self._prefetch_done:
            self._prefetch_related_objects()

    def aggregate(self, *args, **kwargs):
        raise NotImplementedError()

    def count(self):
        """
        Count the total number of objects matching this query.

        Unlike in the regular QuerySet, it's not possible to do a count query
        in Elasticsearch.

        Returns:
            int: The number of objects.
        """
        if self._total is None:
            self._fetch_all()

        return self._total

    def get(self, *args, **kwargs):
        """
        Performs the query and returns a single object matching the given
        keyword arguments.
        """
        clone = self.filter(*args, **kwargs)
        if self.query.can_filter():
            clone = clone.order_by()

        results = list(clone._sql_iterator())

        num = len(results)
        if num == 1:
            return results[0]
        if not num:
            raise self.model.DoesNotExist(
                "%s matching query does not exist." %
                self.model._meta.object_name
            )
        raise self.model.MultipleObjectsReturned(
            "get() returned more than one %s -- it returned %s!" %
            (self.model._meta.object_name, num)
        )

    def _earliest_or_latest(self, field_name=None, direction="-"):
        raise NotImplementedError

    def first(self):
        raise NotImplementedError

    def last(self):
        raise NotImplementedError

    def _filter_or_exclude(self, negate, *args, **kwargs):
        """
        Add filter/exclude queries to Elasticsearch.

        Elasticsearch does not support the full Django filter API, but most
        common filters are supported. This method will convert Django filters
        to their Elasticsearch counterparts.
        """
        clone = super(ElasticQuerySet, self)._filter_or_exclude(negate, *args, **kwargs)

        if len(args) == 0 and len(kwargs) == 0:
            return clone

        queries = []

        for key, value in kwargs.iteritems():
            method = key.split('__')[-1]

            # Detect whether we're dealing with a "special" filter here.
            if method in (
                    'gte', 'gt', 'lt', 'lte', 'exact', 'iexact', 'contains', 'icontains', 'in', 'startswith',
                    'istartswith', 'endswith', 'iendswith', 'range', 'year', 'month', 'day', 'hour', 'minute',
                    'second', 'isnull', 'search', 'regex', 'iregex'
            ):
                field = str(key.replace('__' + method, ''))

                if method in ('gte', 'gt', 'lt', 'lte'):
                    query = Range(**{method: {field: value}})
                elif method == 'exact':
                    query = Term(**{field: value})
                elif method == 'in':
                    query = Terms(**{field: value})
                elif method == 'startswith':
                    query = Prefix(**{field: value})
                elif method == 'range':
                    raise NotImplementedError('Still need to check how range params are passed ;)')
                elif method == 'year':
                    # We can filter on years by rounding the times to years
                    # and then do a range query.
                    query = Range(**{field: {'gte': {value+'/y'}, 'lt': {value+'/y'}}})
                elif method == 'isnull':
                    query = ~Exists(field=field)
                elif method == 'regex':
                    query = Regexp(**{field: value})
                else:
                    raise NotImplementedError('Elasticsearch does not support %s filters.' % method)
            else:
                # This is not a special query, so execute it as a term query.
                query = Term(**{key: value})

            if negate:
                queries.append(~query)
            else:
                queries.append(query)

        clone.search = clone.search.query(Bool(filter=queries))

        return clone

    def order_by(self, *field_names):
        """
        Order the models by the given field names with Elasticsearch.

        Args:
            *field_names: The names of fields to order by.

        Returns:
            ElasticQuerySet: A clone of itself with the ordering.
        """
        assert self.query.can_filter(), \
            "Cannot reorder a query once a slice has been taken."
        obj = self._clone()
        obj.search = obj.search.sort()

        fields = list(field_names)
        if 'id' in fields:
            fields.remove('id')

        if len(fields) > 0:
            obj.search = obj.search.sort(*fields)

        return obj

    def extra(self, select=None, where=None, params=None, tables=None,
              order_by=None, select_params=None):
        """
        Elasticsearch does not support tacking on custom SQL queries.
        """
        raise NotImplementedError('Elasticsearch does not support custom SQL.')

    def _clone(self, klass=None, setup=False, **kwargs):
        """
        Clone the QuerySet but preserve the Elasticsearch Search request.
        """
        obj = super(ElasticQuerySet, self)._clone(klass=klass, setup=setup, **kwargs)
        obj.search = self.search
        return obj

    def elasticsearch_query(self, *args, **kwargs):
        """
        Add an Elasticsearch query object to the QuerySet.

        Useful when utilizing the full text search capabilities of
        Elasticsearch outside the QuerySet API.
        """
        obj = self._clone()
        obj.search = obj.search.query(*args, **kwargs)
        return obj


class ElasticManager(models.Manager):
    def get_queryset(self):
        """
        Get the QuerySet

        Returns:
            ElasticQuerySet: The QuerySet for this manager.
        """
        return ElasticQuerySet(self.model, using=self._db, hints=self._hints)


class ElasticTenantManager(ElasticManager):
    def get_queryset(self):
        """
        Manipulate the returned queryset by adding a filter for tenant using the tenant linked
        to the current logged in user (received via custom middleware).
        """
        user = get_current_user()
        if user and user.is_authenticated():
            return super(ElasticTenantManager, self).get_queryset().filter(tenant_id=user.tenant_id)
        else:
            return super(ElasticTenantManager, self).get_queryset()
