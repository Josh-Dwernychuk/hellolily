from django_elasticsearch_dsl import BooleanField, DateField, IntegerField, ObjectField, TextField
from django_elasticsearch_dsl import Index
from django_elasticsearch_dsl import DocType
from lily.utils.functions import format_phone_number
from .models import Account as AccountModel

index = Index('account')


@index.doc_type
class Account(DocType):
    address_full = TextField()
    address = ObjectField(properties={
        'address': TextField(),
        'postal_code': TextField(),
        'city': TextField(),
        'country': TextField(),
    })
    assigned_to = ObjectField(properties={
        'id': IntegerField(),
        'full_name': TextField(),
    })
    customer_id = TextField()
    created = DateField()
    description = TextField()
    email_addresses = ObjectField(properties={
        'id': IntegerField(),
        'email_address': TextField(),
        'status': IntegerField(),
    })
    is_deleted = BooleanField()
    modified = DateField()
    name = TextField()
    phone_numbers = ObjectField(properties={
        'id': IntegerField(),
        'number': TextField(),
        'type': TextField(),
        'status': IntegerField(),
        'status_name': TextField(),
    })
    status = TextField()
    tags = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
        'object_id': IntegerField(),
    })
    tenant_id = IntegerField()
    domains = TextField()

    def get_queryset(self):
        return AccountModel.objects.all()

    def prepare_address_full(self, obj):
        return [address.full() for address in obj.addresses.all()]

    def prepare_address(self, obj):
        return [{
            'address': address.address,
            'postal_code': address.postal_code,
            'city': address.city,
            'country': address.get_country_display() if address.country else None,
        } for address in obj.addresses.all()]

    def prepare_assigned_to(self, obj):
        return {
            'id': obj.assigned_to.id,
            'full_name': obj.assigned_to.full_name,
        } if obj.assigned_to else None

    def prepare_email_addresses(self, obj):
        return [{
            'id': email.id,
            'email_address': email.email_address,
            'status': email.status,
        } for email in obj.email_addresses.all()]

    def prepare_phone_numbers(self, obj):
        return [{
            'id': phone_number.id,
            'number': format_phone_number(phone_number.number),
            'type': phone_number.type,
            'status': phone_number.status,
            'status_name': phone_number.get_status_display(),
        } for phone_number in obj.phone_numbers.all()]

    def prepare_status(self, obj):
        return obj.status.name if obj.status else None

    def prepare_social_media(self, obj):
        return [{
            'id': soc.id,
            'name': soc.get_name_display(),
            'username': soc.username,
            'profile_url': soc.profile_url
        } for soc in obj.social_media.all()]

    def prepare_tags(self, obj):
        return [{
            'id': tag.id,
            'name': tag.name,
            'object_id': tag.object_id,
        } for tag in obj.tags.all()]

    def prepare_website(self, obj):
        return [{
            'id': website.id,
            'website': website.website,
            'is_primary': website.is_primary,
        } for website in obj.websites.all()]

    def prepare_domains(self, obj):
        return [website.full_domain for website in obj.websites.all()]

    class Meta:
        model = AccountModel
