from django_elasticsearch_dsl import BooleanField, DateField, IntegerField, KeywordField, ObjectField, TextField
from django_elasticsearch_dsl import Index
from django_elasticsearch_dsl import DocType
from .models import Case as CaseModel

index = Index('case')


@index.doc_type
class Case(DocType):
    account = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
        'is_deleted': BooleanField(),
    })
    assigned_to = TextField()
    assigned_to_teams = IntegerField()
    contact = ObjectField(properties={
        'id': IntegerField(),
        'full_name': TextField(),
        'is_deleted': BooleanField(),
    })
    created = DateField()
    created_by = ObjectField(properties={
        'id': IntegerField(),
        'first_name': KeywordField(),
        'full_name': TextField(),
        'last_name': KeywordField(),
    })
    description = TextField()
    expires = DateField()
    is_archived = BooleanField()
    is_deleted = BooleanField()
    modified = DateField()
    newly_assigned = BooleanField()
    priority = IntegerField()
    priority_display = TextField()
    status = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
    })
    subject = TextField()
    tags = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
        'object_id': IntegerField(),
    })
    tenant_id = IntegerField()
    type = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
    })

    def get_queryset(self):
        return CaseModel.objects.all()

    def prepare_assigned_to(self, obj):
        return obj.assigned_to.full_name if obj.assigned_to else None

    def prepare_assigned_to_teams(self, obj):
        return [team.id for team in obj.assigned_to_teams.all()]

    def prepare_contact(self, obj):
        return {
            'id': obj.contact.id,
            'full_name': obj.contact.full_name,
            'is_deleted': obj.contact.is_deleted,
        } if obj.contact else None

    def prepare_is_deleted(self, obj):
        return bool(obj.deleted)

    def prepare_priority_display(self, obj):
        return obj.get_priority_display()

    class Meta:
        model = CaseModel
