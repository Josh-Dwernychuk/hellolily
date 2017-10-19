from django_elasticsearch_dsl import BooleanField, DateField, IntegerField, KeywordField, ObjectField, TextField
from django_elasticsearch_dsl import Index
from django_elasticsearch_dsl import DocType
from lily.utils.functions import format_phone_number
from .models import Contact as ContactModel

index = Index('contact')


@index.doc_type
class Contact(DocType):
    accounts = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
        'customer_id': KeywordField(),
        'function': KeywordField(),
        'phone_numbers': TextField(),
    })
    active_at = IntegerField()
    created = DateField()
    description = TextField()
    email_address = ObjectField(properties={
        'id': IntegerField(),
        'email_address': TextField(),
        'status': IntegerField(),
    })
    first_name = KeywordField()
    full_name = TextField()
    is_deleted = BooleanField()
    last_name = KeywordField()
    modified = DateField()
    phone_numbers = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
        'object_id': IntegerField(),
    })
    tags = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
        'object_id': IntegerField(),
    })
    tenant_id = IntegerField()

    def get_queryset(self):
        return ContactModel.objects.all()

    def _convert_function_to_account(self, func):
        return {
            'id': func.account_id,
            'name': func.account.name if func.account.name else '',
            'customer_id': func.account.customer_id,
            'function': func.title,
            'is_active': func.is_active,
            'phone_numbers': [phone_number.number for phone_number in func.account.phone_numbers.all()],
        }

    def prepare_accounts(self, obj):
        functions = obj.functions.filter(account__is_deleted=False)

        return [self._convert_function_to_account(func) for func in functions]

    def prepare_active_at(self, obj):
        return [f.account_id for f in obj.functions.filter(account__is_deleted=False) if f.is_active]

    def prepare_email_address(self, obj):
        return [{
            'id': email.id,
            'email_address': email.email_address,
            'status': email.status,
        } for email in obj.email_addresses.all()]

    def prepare_phone_numbers(self, obj):
        return [{
            'id': phone_number.id,
            'number': phone_number.number,
            'formatted_number': format_phone_number(phone_number.number),
            'type': phone_number.type,
            'status': phone_number.status,
            'status_name': phone_number.get_status_display(),
        } for phone_number in obj.phone_numbers.all()]

    def prepare_tags(self, obj):
        return [{
            'id': tag.id,
            'name': tag.name,
            'object_id': tag.object_id,
        } for tag in obj.tags.all()]

    class Meta:
        model = ContactModel
