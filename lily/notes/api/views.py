from django_filters import CharFilter
from rest_framework.filters import DjangoFilterBackend, FilterSet, OrderingFilter
from rest_framework.viewsets import ModelViewSet

from lily.api.filters import ElasticSearchFilter
from lily.notes.api.serializers import NoteSerializer
from lily.notes.models import Note


class NoteFilter(FilterSet):
    content_type = CharFilter(name='content_type__model')

    class Meta:
        model = Note
        fields = ('object_id', 'content_type', 'is_pinned')


class NoteViewSet(ModelViewSet):
    """
    This viewset contains all possible ways to manipulate a Note.
    """
    model = Note
    queryset = Note.elastic_objects  # Without .all() this filters on the tenant
    serializer_class = NoteSerializer

    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, DjangoFilterBackend)
    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('created',)
    # DjangoFilterBackend: set the possible fields to filter on.
    filter_class = NoteFilter
    # SearchFilter: the fields to search.
    search_fields = ('author', 'content')

    def get_queryset(self, *args, **kwargs):
        return super(NoteViewSet, self).get_queryset().filter(is_deleted=False)
