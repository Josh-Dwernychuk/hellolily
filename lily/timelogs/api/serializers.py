from rest_framework import serializers

from ..models import TimeLog


class TimeLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the TimeLog model.
    """
    # Show string versions of fields.
    user = serializers.StringRelatedField(read_only=True)
    date = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        user = self.context.get('request').user

        validated_data.update({
            'user': user,
        })

        return super(TimeLogSerializer, self).create(validated_data)

    class Meta:
        model = TimeLog
        fields = (
            'id',
            'billable',
            'content',
            'date',
            'gfk_content_type',
            'gfk_object_id',
            'hours_logged',
            'user',
        )
