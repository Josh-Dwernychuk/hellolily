from rest_framework import serializers

from ..models import EmailLabel, EmailAccount, EmailMessage, Recipient, EmailAttachment


class EmailLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLabel
        fields = ('id', 'account', 'label_type', 'label_id', 'name', 'unread')


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = ('id', 'name', 'email_address')


class EmailAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAttachment
        fields = ('id', 'inline', 'attachment', 'size', 'message')


class EmailMessageSerializer(serializers.ModelSerializer):
    sender = RecipientSerializer(many=False, read_only=True)
    received_by = RecipientSerializer(many=True, read_only=True)
    received_by_cc = RecipientSerializer(many=True, read_only=True)
    attachments = EmailAttachmentSerializer(many=True, read_only=True)
    labels = EmailLabelSerializer(many=True, read_only=True)
    sent_date = serializers.ReadOnlyField()

    class Meta:
        model = EmailMessage
        fields = (
            'id',
            'labels',
            'sent_date',
            'body_html',
            'body_text',
            'received_by',
            'received_by_cc',
            'sender',
            'attachments',
            'read',
        )


class EmailAccountSerializer(serializers.ModelSerializer):
    labels = EmailLabelSerializer(many=True, read_only=True)

    class Meta:
        model = EmailAccount
        fields = ('id', 'email_address', 'labels', 'label')

