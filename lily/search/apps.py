from django_elasticsearch_dsl.apps import DEDConfig
from django_elasticsearch_dsl.signals import RealTimeSignalProcessor
from elasticsearch_dsl.connections import connections


class SearchConfig(DEDConfig):
    name = 'lily.search'
    signal_processor = RealTimeSignalProcessor(connections)

    def ready(self):
        self.module.autodiscover()
        super(SearchConfig, self).ready()
