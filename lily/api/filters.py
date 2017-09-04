from elasticsearch_dsl.query import MultiMatch, QueryString
from rest_framework.filters import BaseFilterBackend, SearchFilter

from lily.search.models import ElasticQuerySet


class ElasticSearchFilter(SearchFilter):

    def filter_queryset(self, request, queryset, view):
        if not isinstance(queryset, ElasticQuerySet):
            AttributeError('ElasticSearchFilter can only be used with a ElasticQuerySet.')

        search_fields = getattr(view, 'search_fields', None)
        search_term = request.query_params.get(self.search_param, '')

        if not search_fields or not search_term:
            return queryset

        return queryset.elasticsearch_query(MultiMatch(query=search_term, fields=list(search_fields)))


class SoftDeleteFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if hasattr(view, 'filter_deleted_attribute'):
            attribute = view.filter_deleted_attribute
        else:
            attribute = 'filter_deleted'

        if attribute in request.GET and request.GET.get(attribute) == 'False':
            return queryset
        else:
            return queryset.filter(is_deleted=False)


class ElasticQueryFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if 'filterquery' in request.GET and request.GET.get('filterquery'):
            return queryset.elasticsearch_query(QueryString(query=request.GET.get('filterquery')))
        else:
            return queryset
