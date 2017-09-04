from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.filters import OrderingFilter, DjangoFilterBackend
from rest_framework.response import Response

from lily.api.filters import ElasticSearchFilter, ElasticQueryFilter, SoftDeleteFilter
from lily.api.mixins import ModelChangesMixin

from lily.calls.api.serializers import CallRecordSerializer
from lily.calls.models import CallRecord
from lily.contacts.api.serializers import ContactSerializer
from lily.contacts.models import Contact, Function
from lily.utils.functions import uniquify


class ContactViewSet(ModelChangesMixin, viewsets.ModelViewSet):
    """
    Returns a list of all **active** contacts in the system.

    #Search#
    Searching is enabled on this API.

    To search, provide a field name to search on followed by the value you want to search for to the search parameter.

    #Ordering#
    Ordering is enabled on this API.

    To order, provide a comma seperated list to the ordering argument. Use `-` minus to inverse the ordering.

    #Examples#
    - plain: `/api/contacts/`
    - search: `/api/contacts/?search=subject:Doremi`
    - order: `/api/contacts/?ordering=subject,-id`

    #Returns#
    * List of cases with related fields
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Contact.elastic_objects
    # Set the serializer class for this viewset.
    serializer_class = ContactSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (SoftDeleteFilter, ElasticQueryFilter, ElasticSearchFilter, OrderingFilter, DjangoFilterBackend)

    # OrderingFilter: set all possible fields to order by.
    ordering_fields = (
        'first_name', 'last_name',
    )
    # OrderingFilter: set the default ordering fields.
    ordering = ('last_name', 'first_name',)
    # SearchFilter: set the fields that can be searched on.
    search_fields = ('full_name', )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['patch', ])
    def toggle_activation(self, request):
        """
        Toggle if the contact is active at account.
        """
        contact_id = request.data.get('contact')
        account_id = request.data.get('account')
        is_active = request.data.get('is_active')

        try:
            func = Function.objects.get(contact=contact_id, account=account_id)
        except Function.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            func.is_active = is_active
            func.save()

            return Response(status=status.HTTP_200_OK)

    @detail_route(methods=['GET', ])
    def calls(self, request, pk=None):
        contact = self.get_object()

        phone_numbers = contact.phone_numbers.all().values_list('number', flat=True)
        phone_numbers = uniquify(phone_numbers)  # Filter out double numbers.

        calls = CallRecord.objects.filter(
            Q(caller__number__in=phone_numbers) | Q(destination__number__in=phone_numbers)
        )

        page = self.paginate_queryset(calls)

        return self.get_paginated_response(
            CallRecordSerializer(page, many=True, context={'request': request}).data
        )
