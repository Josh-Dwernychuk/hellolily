from django.contrib import admin

from lily.messaging.email.models import EmailProvider, EmailAccount, EmailMessage

admin.site.register(EmailProvider)
admin.site.register(EmailAccount)
admin.site.register(EmailMessage)