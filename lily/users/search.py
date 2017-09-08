from lily.search.base_mapping import BaseMapping
from lily.search.fields import TextField, KeywordField, BooleanField, IntegerField
from lily.search.indices import Index
from lily.search.search import DocType

from .models import LilyUser as LilyUserModel, Team as TeamModel

user_index = Index('user')
team_index = Index('user_team')


class LilyUserMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return LilyUserModel

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        mapping = super(LilyUserMapping, cls).get_mapping()
        mapping['properties'].update({
            'first_name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'last_name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'full_name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'position': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'is_active': {
                'type': 'boolean',
            },
            'email': {
                'type': 'string',
                'analyzer': 'email_analyzer',
            },
            'phone_number': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'internal_number': {
                'type': 'integer',
                'index_analyzer': 'simple',
            },
            'teams': {
                'type': 'integer',
            },
        })
        return mapping

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        return {
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'full_name': obj.full_name,
            'position': obj.position,
            'profile_picture': obj.profile_picture,
            'email': obj.email,
            'is_active': obj.is_active,
            'phone_number': obj.phone_number,
            'internal_number': obj.internal_number,
            'teams': [team.id for team in obj.teams.all()],
        }


class TeamMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return TeamModel

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        mapping = super(TeamMapping, cls).get_mapping()
        mapping['properties'].update({
            'name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
        })
        return mapping

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        return {
            'name': obj.name,
        }


@user_index.doc_type
class LilyUser(DocType):
    first_name = KeywordField()
    last_name = KeywordField()
    full_name = TextField()
    position = TextField()
    is_active = BooleanField()
    email = TextField()
    phone_number = TextField()
    internal_number = KeywordField()
    teams = IntegerField()
    tenant_id = IntegerField()

    def get_queryset(self):
        return LilyUserModel.objects.all()

    def prepare_teams(self, obj):
        return [team.id for team in obj.teams.all()]

    class Meta:
        model = LilyUserModel


@team_index.doc_type
class Team(DocType):
    name = TextField()

    def get_queryset(self):
        return TeamModel.objects.all()

    class Meta:
        model = TeamModel
