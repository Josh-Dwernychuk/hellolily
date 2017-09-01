from django.apps import AppConfig
from django.conf import settings

from elasticsearch_dsl.connections import connections

from .utils import import_class


class SearchConfig(AppConfig):
    name = 'lily.search'
    signal_processor = None

    def ready(self):
        self.module.autodiscover()
        connections.configure(**settings.ELASTICSEARCH_DSL)
        # Setup the signal processor.
        if not self.signal_processor:
            signal_processor_path = getattr(
                settings,
                'ELASTICSEARCH_DSL_SIGNAL_PROCESSOR',
                'lily.search.signals.RealTimeSignalProcessor'
            )
            signal_processor_class = import_class(signal_processor_path)
            self.signal_processor = signal_processor_class(connections)

    @classmethod
    def autosync_enabled(cls):
        return getattr(settings, 'ELASTICSEARCH_DSL_AUTOSYNC', True)

    @classmethod
    def default_index_settings(cls):
        return getattr(settings, 'ELASTICSEARCH_DSL_INDEX_SETTINGS', {})

    @classmethod
    def auto_refresh_enabled(cls):
        return getattr(settings, 'ELASTICSEARCH_DSL_AUTO_REFRESH', True)
