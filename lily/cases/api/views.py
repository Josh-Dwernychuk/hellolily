from django_filters import CharFilter
from django_filters.rest_framework import BooleanFilter, DateFilter, DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from rest_framework_filters import FilterSet

from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ModelChangesMixin
from .serializers import CaseSerializer, CaseStatusSerializer, CaseTypeSerializer
from ..models import Case, CaseStatus, CaseType


class CaseFilter(FilterSet):
    """
    Class to filter case queryset.
    """
    type = CharFilter(name='type__type')
    status = CharFilter(name='status__status')
    not_type = CharFilter(name='type__type', exclude=True)
    not_status = CharFilter(name='status__status', exclude=True)
    is_archived = BooleanFilter()
    expires = DateFilter()

    class Meta:
        model = Case
        fields = {
            'type': ['exact'],
            'status': ['exact'],
            'not_type': ['exact'],
            'not_status': ['exact'],
            'is_archived': ['exact'],
            'expires': ['exact', 'gte', 'lte', 'lt', 'gt'],
            'account__id': ['exact'],
        }


class CaseViewSet(ModelChangesMixin, viewsets.ModelViewSet):
    """
    Returns a list of all **active** cases in the system.

    #Search#
    Searching is enabled on this API.

    To search, provide a field name to search on followed by the value you want to search for to the search parameter.

    #Filtering#
    Filtering is enabled on this API.

    To filter, use the field name as parameter name followed by the value you want to filter on.

    #Ordering#
    Ordering is enabled on this API.

    To order, provide a comma seperated list to the ordering argument. Use `-` minus to inverse the ordering.

    #Examples#
    - plain: `/api/cases/`
    - search: `/api/cases/?search=subject:Doremi`
    - filter: `/api/cases/?type=1`
    - order: `/api/cases/?ordering=subject,-id`

    #Returns#
    * List of cases with related fields
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Case.elastic_objects
    # Set the serializer class for this viewset.
    serializer_class = CaseSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, DjangoFilterBackend)

    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('created', 'modified', 'type', 'status__id', 'assigned_to', 'priority', 'subject', 'expires',
                       'created_by__first_name')
    # SearchFilter: set the fields that can be searched on.
    search_fields = ('account__name', 'contact__full_name', 'assigned_to', 'created_by__full_name', 'status__name',
                     'subject', 'tags__name', 'type__name',)
    # DjangoFilter: set the filter class.
    filter_class = CaseFilter

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(CaseViewSet, self).get_queryset().filter(is_deleted=False)


class TeamsCaseList(APIView):
    """
    List all cases assigned to the current users teams.
    """
    model = Case
    serializer_class = CaseSerializer
    filter_class = CaseFilter

    def get_queryset(self):
        return self.model.objects.filter(tenant_id=self.request.user.tenant_id)


class CaseStatusViewSet(viewsets.ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = CaseStatus.objects
    # Set the serializer class for this viewset.
    serializer_class = CaseStatusSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(CaseStatusViewSet, self).get_queryset().all()


class CaseTypeViewSet(viewsets.ModelViewSet):
    model = CaseType
    queryset = CaseType.objects
    serializer_class = CaseTypeSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        queryset = super(CaseTypeViewSet, self).get_queryset().filter(tenant_id=self.request.user.tenant_id)

        # By default we filter out non-active users.
        is_archived = self.request.query_params.get('is_archived', 'False')

        # Value must be one of these, or it is ignored and we filter out non-active users.
        if is_archived not in ['All', 'True', 'False']:
            is_archived = 'False'

        if is_archived in ['True', 'False']:
            queryset = queryset.filter(is_archived=(is_archived == 'True'))

        return queryset
