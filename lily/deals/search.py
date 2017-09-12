from lily.search.fields import BooleanField, DateField, FloatField, IntegerField, KeywordField, ObjectField, TextField
from lily.search.indices import Index
from lily.search.search import DocType
from .models import Deal as DealModel

index = Index('deal')


@index.doc_type
class Deal(DocType):
    account = ObjectField(properties={
        'id': IntegerField(),
        'customer_id': TextField(),
        'name': TextField(),
        'is_deleted': BooleanField(),
    })
    amount_once = FloatField()
    amount_recurring = FloatField()
    assigned_to = ObjectField(properties={
        'id': IntegerField(),
        'first_name': KeywordField(),
        'full_name': TextField(),
        'last_name': KeywordField(),
    })
    assigned_to_teams = IntegerField()
    card_sent = BooleanField()
    closed_date = DateField()
    contact = ObjectField(properties={
        'id': IntegerField(),
        'full_name': TextField(),
        'is_deleted': BooleanField(),
    })
    contacted_by = ObjectField(properties={
        'id': IntegerField(),
        'full_name': TextField(),
    })
    created = DateField()
    created_by = ObjectField(properties={
        'id': IntegerField(),
        'first_name': KeywordField(),
        'full_name': TextField(),
        'last_name': KeywordField(),
    })
    currency = KeywordField()
    currency_display = KeywordField()
    description = TextField()
    found_through = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
    })
    is_archived = BooleanField()
    is_checked = BooleanField()
    is_deleted = BooleanField()
    modified = DateField()
    name = TextField()
    new_business = BooleanField()
    newly_assigned = BooleanField()
    next_step = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
        'date_increment': IntegerField(),
        'position': IntegerField(),
    })
    next_step_date = DateField(fields={
        'sortable': DateField()
    })
    quote_id = KeywordField()
    status = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
        'position': IntegerField(),
    })
    tags = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
        'object_id': IntegerField(),
    })
    tenant_id = IntegerField()
    twitter_checked = BooleanField()
    why_customer = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
    })
    why_lost = TextField()

    def get_queryset(self):
        return DealModel.objects.all()

    def prepare_account(self, obj):
        return {
            'id': obj.account.id,
            'name': obj.account.name,
            'customer_id': obj.account.customer_id,
            'is_deleted': obj.account.is_deleted,
        } if obj.account else None

    def prepare_assigned_to(self, obj):
        return {
            'id': obj.assigned_to.id,
            'first_name': obj.assigned_to.first_name,
            'full_name': obj.assigned_to.full_name,
            'last_name': obj.assigned_to.last_name,
        } if obj.assigned_to else None

    def prepare_assigned_to_teams(self, obj):
        return [team.id for team in obj.assigned_to_teams.all()]

    def prepare_contact(self, obj):
        return {
            'id': obj.contact.id,
            'first_name': obj.contact.first_name,
            'full_name': obj.contact.full_name,
            'is_deleted': obj.contact.is_deleted,
            'last_name': obj.contact.last_name,
        } if obj.contact else None

    def prepare_contacted_by(self, obj):
        return {
            'id': obj.contacted_by.id,
            'name': obj.contacted_by.name,
        } if obj.contacted_by else None

    def prepare_content_type(self, obj):
        return obj.content_type.id

    def prepare_created_by(self, obj):
        return {
            'id': obj.created_by.id,
            'full_name': obj.created_by.full_name,
        } if obj.created_by else None

    def prepare_currency_display(self, obj):
        return obj.get_currency_display()

    def prepare_found_through(self, obj):
        return {
            'id': obj.found_through.id,
            'name': obj.found_through.name,
        } if obj.found_through else None

    def prepare_is_deleted(self, obj):
        return obj.is_deleted

    def prepare_next_step(self, obj):
        return {
            'id': obj.next_step.id,
            'name': obj.next_step.name,
            'date_increment': obj.next_step.date_increment,
            'position': obj.next_step.position,
        } if obj.next_step else None

    def prepare_tags(self, obj):
        return [{
            'id': tag.id,
            'name': tag.name,
            'object_id': tag.object_id,
        } for tag in obj.tags.all()]

    def prepare_why_customer(self, obj):
        return {
            'id': obj.why_customer.id,
            'name': obj.why_customer.name,
        } if obj.why_customer else None

    def prepare_why_lost(self, obj):
        return obj.why_lost.name if obj.why_lost else None

    class Meta:
        model = DealModel
