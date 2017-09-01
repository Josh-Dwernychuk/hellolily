from django.utils.module_loading import autodiscover_modules
from django_elasticsearch_dsl import signals  # noqa


def autodiscover():
    autodiscover_modules('search')


default_app_config = 'lily.search.apps.SearchConfig'
