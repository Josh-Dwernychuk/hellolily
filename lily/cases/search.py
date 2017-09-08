from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.search.base_mapping import BaseMapping
from lily.search.fields import ObjectField, BooleanField, IntegerField, TextField, DateField
from lily.search.indices import Index
from lily.search.search import DocType
from lily.tags.models import Tag

from .models import Case as CaseModel

index = Index('case')


class CaseMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return CaseModel

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        mapping = super(CaseMapping, cls).get_mapping()
        mapping['properties'].update({
            'account': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'is_deleted': {'type': 'boolean'},
                },
            },
            'assigned_to': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'full_name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'assigned_to_teams': {
                'type': 'integer',
            },
            'contact': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'is_deleted': {'type': 'boolean'},
                },
            },
            'created': {
                'type': 'date',
            },
            'created_by': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'full_name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'description': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'expires': {
                'type': 'date',
            },
            'is_archived': {
                'type': 'boolean',
            },
            'modified': {
                'type': 'date',
            },
            'newly_assigned': {
                'type': 'boolean',
            },
            'priority': {
                'type': 'integer',
            },
            'priority_display': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'status': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'subject': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'tags': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer',
                    },
                    'object_id': {'type': 'integer'},
                },
            },
            'type': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer',
                    },
                },
            },
        })
        return mapping

    @classmethod
    def get_related_models(cls):
        """
        Maps related models, how to get an instance list from a signal sender.
        """
        return {
            Contact: lambda obj: obj.case_set.all(),
            Account: lambda obj: obj.case_set.all(),
            Tag: lambda obj: [obj.subject],
        }

    @classmethod
    def prepare_batch(cls, queryset):
        """
        Optimize a queryset for batch indexing.
        """
        return queryset.prefetch_related(
            'status',
            'type',
            'account',
            'contact',
            'assigned_to',
            'tags',
        )

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        return {
            'account': {
                'id': obj.account.id,
                'name': obj.account.name,
                'is_deleted': obj.account.is_deleted,
            } if obj.account else None,
            'assigned_to': {
                'id': obj.assigned_to.id,
                'full_name': obj.assigned_to.full_name,
            } if obj.assigned_to else None,
            'assigned_to_teams': [team.id for team in obj.assigned_to_teams.all()],
            'contact': {
                'id': obj.contact.id,
                'full_name': obj.contact.full_name,
                'is_deleted': obj.contact.is_deleted,
            } if obj.contact else None,
            'content_type': obj.content_type.id,
            'created': obj.created,
            'created_by': {
                'id': obj.created_by.id,
                'full_name': obj.created_by.full_name,
            } if obj.created_by else None,
            'description': obj.description,
            'expires': obj.expires,
            'is_archived': obj.is_archived,
            'modified': obj.modified,
            'newly_assigned': obj.newly_assigned,
            'priority': obj.priority,
            'priority_display': obj.get_priority_display(),
            'status': {
                'id': obj.status.id,
                'name': obj.status.name,
            },
            'subject': obj.subject,
            'tags': [{
                'id': tag.id,
                'name': tag.name,
                'object_id': tag.object_id,
            } for tag in obj.tags.all()],
            'type': {
                'id': obj.type.id,
                'name': obj.type.name,
            } if obj.type else None,
            'parcel_provider': obj.parcel.get_provider_display() if obj.parcel else None,
            'parcel_identifier': obj.parcel.identifier if obj.parcel else None,
            'parcel_link': obj.parcel.get_link() if obj.parcel else None,
        }


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
        'name': TextField(),
        'is_deleted': BooleanField(),
    })
    created = DateField()
    created_by = ObjectField(properties={
        'id': IntegerField(),
        'full_name': TextField(),
    })
    description = TextField()
    expires = DateField()
    is_archived = BooleanField()
    is_deleted = BooleanField()
    modified = DateField()
    newly_assigned = BooleanField()
    priority = IntegerField()
    priority_display = TextField()
    status = TextField()
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

    def prepare_status(self, obj):
        return obj.status.name

    def prepare_tenant_id(self, obj):
        return obj.tenant_id

    class Meta:
        model = CaseModel
