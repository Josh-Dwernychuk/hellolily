from django.conf.urls import url

from .views import SearchView, PhoneNumberSearchView


urlpatterns = [
    url(r'^search/$', SearchView.as_view(), name='search_view'),
    url(r'^number/(?P<number>(\+)?([\d\-]+))$',
        PhoneNumberSearchView.as_view(),
        name='search_view'),
]
