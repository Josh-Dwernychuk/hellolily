from unittest import TestCase
import datetime

from django.utils.timezone import make_aware
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, MultiMatch
from mock import MagicMock

from lily.cases.factories import CaseFactory
from lily.cases.models import Case
from lily.search.models import ElasticQuerySet
from lily.search.registries import registry


class ElasticQuerySetTestCase(TestCase):
    def setUp(self):
        self.model_class = Case
        self.model_factory = CaseFactory
        self.search_field = 'subject'
        self.queryset_with_search = ElasticQuerySet(self.model_class).elasticsearch_query(Match(foo='bar'))

    def get_query_set_with_full_text_search(self):
        return ElasticQuerySet(self.model_class).elasticsearch_query(MultiMatch(query='test', fields=['foo', 'bar']))

    def test___init_(self):
        """
        ElasticQuerySet init creates a new search object.
        """
        qs = ElasticQuerySet(self.model_class)

        self.assertIsInstance(qs.search, Search)

    def test__has_full_text_search_no_search(self):
        """
        _has_full_text_search returns false if the QS lacks full text search.
        """
        self.assertFalse(ElasticQuerySet()._has_full_text_search)

    def test__has_full_text_search_match(self):
        """
        _has_full_text_search returns true if the QS has a match query.
        """
        self.assertTrue(ElasticQuerySet(self.model_class).elasticsearch_query(Match(foo='bar'))._has_full_text_search)

    def test__has_full_text_search_multi_match(self):
        """
        _has_full_text_search returns true if the QS has a multi match query.
        """
        self.assertTrue(self.get_query_set_with_full_text_search()._has_full_text_search)

    def test__has_full_text_search_filter(self):
        """
        _has_full_text_search returns false if the QS has a filter query.
        """
        qs = ElasticQuerySet(self.model_class)
        qs.search = qs.search.filter(foo='bar')

        self.assertFalse(qs._has_full_text_search)

    def test__has_full_text_search_filter_multi_match(self):
        """
        _has_full_text_search returns true if QS has filter and match query.
        """
        qs = self.get_query_set_with_full_text_search()
        qs.search = qs.search.filter(fux='baz')

        self.assertTrue(qs._has_full_text_search)

    def test_first_uses_elasticsearch_for_full_text(self):
        """
        first uses Elasticsearch if the query has full text search.
        """
        model = self.model_factory.create()
        qs = ElasticQuerySet(self.model_class).elasticsearch_query(
            Match(**{self.search_field: getattr(model, self.search_field)})
        )
        qs.search.execute = MagicMock(wraps=qs.search.execute)

        result = qs.first()

        qs.search.execute.assert_called_once_with(ignore_cache=True)

        self.assertEqual(model, result)

    def test_first_uses_sql_without_full_text_search(self):
        """
        first doesn't use Elasticsearch if there is no full text search.
        """
        qs = ElasticQuerySet(self.model_class)
        qs.search.execute = MagicMock(wraps=qs.search.execute)

        qs.first()

        qs.search.execute.assert_not_called()

    def test_last(self):
        """
        last is not supported on ElasticQuerySet.
        """
        qs = ElasticQuerySet(self.model_class)
        self.assertRaises(NotImplementedError, qs.last)

    def test_count_uses_elasticsearch_full_text(self):
        """
        count uses Elasticsearch if a query has full text search.
        """
        qs = ElasticQuerySet(self.model_class).elasticsearch_query(MultiMatch(query='test', fields=['foo', 'bar']))
        qs.search.execute = MagicMock(wraps=qs.search.execute)
        qs.query.get_count = MagicMock(wraps=qs.query.get_count)

        qs.count()

        qs.search.execute.assert_called_once()
        qs.query.get_count.assert_not_called()

    def test_count_uses_sql_without_full_text(self):
        """
        count uses SQL if a query does not have full text search.
        """
        qs = ElasticQuerySet(self.model_class)
        qs.search.execute = MagicMock(wraps=qs.search.execute)
        qs.query.get_count = MagicMock(wraps=qs.query.get_count)

        qs.count()

        qs.search.execute.assert_not_called()
        qs.query.get_count.assert_called_once()

    def test___getitem__uses_elasticsearch_full_text_slice(self):
        """
        qs[start:stop] uses Elasticsearch for full text search.
        """
        qs = ElasticQuerySet(self.model_class).elasticsearch_query(MultiMatch(query='test', fields=['foo', 'bar']))

        result = qs[10:15]
        search_dict = result.search.to_dict()
        self.assertEqual(10, search_dict['from'])
        self.assertEqual(5, search_dict['size'])

    def test___getitem___elasticsearch_start_from_zero(self):
        """
        qs[:stop] will use 0 as starting element.
        """
        qs = ElasticQuerySet(self.model_class).elasticsearch_query(MultiMatch(query='test', fields=['foo', 'bar']))

        result = qs[:1337]
        search_dict = result.search.to_dict()
        self.assertEqual(0, search_dict['from'])
        self.assertEqual(1337, search_dict['size'])

    def test___getitem__elasticsearch_takes_upto_10k_items(self):
        """
        qs[start:] will take up to 10k items (the max for ES).
        """
        qs = ElasticQuerySet(self.model_class).elasticsearch_query(MultiMatch(query='test', fields=['foo', 'bar']))

        result = qs[50:]
        search_dict = result.search.to_dict()
        self.assertEqual(50, search_dict['from'])
        self.assertEqual(10000, search_dict['size'])

    def test___getitem__uses_elasticsearch_full_text_index(self):
        """
        qs[k] uses Elasticsearch for full text search.
        """
        model = self.model_factory.create()

        for index in registry.get_indices([model.__class__]):
            index.refresh()

        qs = ElasticQuerySet(self.model_class).elasticsearch_query(
            Match(**{self.search_field: getattr(model, self.search_field)})
        )
        qs.search.__getitem__ = MagicMock(wraps=qs.search.__getitem__)

        result = qs[0]

        self.assertIsNotNone(result)
        # TODO: Verify that Elasticsearch was actually used.
        # Unfortunately, the search instance is cloned, so you can't actually
        # patch and wrap the search executor. May have to try something with
        # a dummy response, but the ES Response is quite complicated.

    def assertFilterEquals(self, search, expected_filter):
        filter_dict = search.to_dict()['query']['bool']['filter']

        self.assertEqual(1, len(filter_dict))
        self.assertEqual(expected_filter, filter_dict[0])

    def test_filter_equals(self):
        """
        Test a filter without a method creates a term query.
        """
        qs = self.get_query_set_with_full_text_search()
        new_qs = qs.filter(id=1337)

        self.assertFilterEquals(new_qs.search, {'term': {'id': 1337}})

    def test_filter_value_compare(self):
        """
        Test gte, gt, lt, lte filter methods create a range query.
        """
        for method in ('gte', 'gt', 'lt', 'lte'):
            qs = self.get_query_set_with_full_text_search()
            new_qs = qs.filter(**{'id__%s' % method: 1337})

            self.assertFilterEquals(new_qs.search, {'range': {'id': {method: 1337}}})

    def test_filter_exact(self):
        """
        Test exact filter method creates a term query.
        """
        qs = self.get_query_set_with_full_text_search()
        new_qs = qs.filter(id__exact=1337)

        self.assertFilterEquals(new_qs.search, {'term': {'id': 1337}})

    def test_filter_in(self):
        """
        Test in filter method creates a terms query.
        """
        qs = self.get_query_set_with_full_text_search()
        new_qs = qs.filter(id__in=[1337, 9001])

        self.assertFilterEquals(new_qs.search, {'terms': {'id': [1337, 9001]}})

    def test_filter_startswith(self):
        """
        Test startswith filter method creates a prefix query.
        """
        qs = self.get_query_set_with_full_text_search()
        new_qs = qs.filter(**{'%s__startswith' % self.search_field: 'foo'})

        self.assertFilterEquals(new_qs.search, {'prefix': {self.search_field: 'foo'}})

    def test_filter_range(self):
        """
        Test range filter method creates a range query.
        """
        start = make_aware(datetime.datetime(2017, 1, 1))
        end = make_aware(datetime.datetime(2017, 12, 31))

        qs = self.get_query_set_with_full_text_search()
        new_qs = qs.filter(created__range=(start, end))

        self.assertFilterEquals(new_qs.search, {'range': {'created': {
            'gte': str(start), 'lte': str(end)
        }}})

    def test_filter_isnull(self):
        """
        Test isnull filter method creates a negated exists query.
        """
        qs = self.get_query_set_with_full_text_search()
        new_qs = qs.filter(**{'%s__isnull' % self.search_field: True})

        self.assertFilterEquals(new_qs.search, {'bool': {'must_not': [{'exists': {'field': self.search_field}}]}})

        qs = self.get_query_set_with_full_text_search()
        new_qs = qs.filter(**{'%s__isnull' % self.search_field: False})

        self.assertFilterEquals(new_qs.search, {'exists': {'field': 'subject'}})

    def test_filter_regex(self):
        """
        Test regex filter method creates a regexp query.
        """
        qs = self.get_query_set_with_full_text_search()
        new_qs = qs.filter(**{'%s__regex' % self.search_field: '\w+'})

        self.assertFilterEquals(new_qs.search, {'regexp': {self.search_field: '\w+'}})

    def test_exclude(self):
        """
        Test exact exclude method creates a negated term query.
        """
        qs = self.get_query_set_with_full_text_search()
        new_qs = qs.exclude(id__exact=1337)

        self.assertFilterEquals(new_qs.search, {'bool': {'must_not': [{'term': {'id': 1337}}]}})

    def test_filter_unsupported_filters(self):
        """
        Test filter raises an exception if an unsupported filter is used.
        """
        for method in (
                'iexact', 'contains', 'icontains', 'istartswith', 'endswith', 'iendswith', 'year', 'month', 'day',
                'hour', 'minute', 'second', 'search', 'iregex'
        ):
            qs = self.get_query_set_with_full_text_search()
            with self.assertRaises(NotImplementedError):
                qs.filter(**{'created__%s' % method: 123})
