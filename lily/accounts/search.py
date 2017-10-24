from django_elasticsearch_dsl import BooleanField, DateField, IntegerField, KeywordField, ObjectField, TextField
from django_elasticsearch_dsl import DocType
from django_elasticsearch_dsl import Index

from lily.utils.functions import format_phone_number
from .models import Account as AccountModel

index = Index('account')


@index.doc_type
class Account(DocType):
    addresses = KeywordField()
    assigned_to = IntegerField()
    assigned_to_full_name = TextField()
    bankaccountnumber = KeywordField()
    bic = KeywordField()
    cocnumber = KeywordField()
    contacts = IntegerField()
    created = DateField()
    customer_id = IntegerField()
    description = KeywordField(fields={
        'text': TextField(),
    })
    domains = KeywordField()
    email_addresses = IntegerField()
    email_addresses_addresses = TextField()
    flatname = KeywordField()
    iban = KeywordField()
    legalentity = KeywordField()
    id = IntegerField()
    is_deleted = BooleanField()
    modified = DateField()
    name = KeywordField(fields={
        'text': TextField()
    })
    phone_numbers = IntegerField()
    phone_numbers_numbers = TextField()
    social_media = IntegerField()
    status = IntegerField()
    tags = TextField()
    taxnumber = KeywordField()
    tenant_id = IntegerField()
    websites = KeywordField()

    def get_queryset(self):
        return AccountModel.objects.all()

    def prepare_addresses(self, obj):
        return [address.full() for address in obj.addresses.all()]

    def prepare_assigned_to(self, obj):
        return obj.assigned_to.id if obj.assigned_to else None

    def prepare_assigned_to_full_name(self, obj):
        return obj.assigned_to.full_name if obj.assigned_to else None

    def prepare_contacts(self, obj):
        return [contact.id for contact in obj.contacts.all()]

    def prepare_domains(self, obj):
        return [website.website for website in obj.websites.all()]

    def prepare_email_addresses(self, obj):
        return [email.id for email in obj.email_addresses.all()]

    def prepare_email_addresses_addresses(self, obj):
        return [email.email_address for email in obj.email_addresses.all()]

    def prepare_phone_numbers(self, obj):
        return [phone_number.id for phone_number in obj.phone_numbers.all()]

    def prepare_phone_numbers_numbers(self, obj):
        return [phone_number.number for phone_number in obj.phone_numbers.all()]

    def prepare_social_media(self, obj):
        return [social_media.id for social_media in obj.social_media.all()]

    def prepare_status(self, obj):
        return obj.status_id

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def prepare_websites(self, obj):
        return [website.id for website in obj.websites.all()]

    class Meta:
        model = AccountModel
