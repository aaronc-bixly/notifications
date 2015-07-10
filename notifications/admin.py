from django.contrib import admin
from django import forms
from django.forms import ValidationError

from notifications.models import NoticeType, NoticeQueueBatch, NoticeSetting, NoticeHistory, DigestSubscription


class NoticeHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ["notice_type", "recipient", "sender", "extra_context", "attachments", "sent_at"]


class NoticeTypeAdmin(admin.ModelAdmin):
    list_display = ["label", "display", "description", "default"]


class NoticeSettingAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "notice_type", "medium", "scoping", "send"]


class DigestSubscriptionAdminForm(forms.ModelForm):
    notice_type_list = forms.ModelChoiceField(queryset=NoticeType.objects.all(), to_field_name="label", required=False)
    notice_type = forms.CharField(max_length=40, required=False)

    class Meta:
        model = DigestSubscription
        fields = ["user", "notice_type_list", "notice_type", "frequency"]
        labels = {
            "notice_type_list": "Notice Type List",
        }

    def clean(self):
        cleaned_data = super(DigestSubscriptionAdminForm, self).clean()
        notice_type_list = cleaned_data.get("notice_type_list")
        notice_type = cleaned_data.get("notice_type")
        if notice_type_list == None and notice_type == '':
            raise ValidationError("You must fill either 'Notice Type List' or 'Notice Type'", code='empty_fields')
        if notice_type_list is not None:
            cleaned_data["notice_type"] = notice_type_list
        return cleaned_data


class DigestSubscriptionAdmin(admin.ModelAdmin):
    form = DigestSubscriptionAdminForm
    list_display = ["user", "notice_type", "frequency"]
    fields = ["user", "notice_type_list", "notice_type", "frequency"]
    readonly_fields = ["emit_at",]


admin.site.register(DigestSubscription, DigestSubscriptionAdmin)
admin.site.register(NoticeQueueBatch)
admin.site.register(NoticeType, NoticeTypeAdmin)
admin.site.register(NoticeSetting, NoticeSettingAdmin)
admin.site.register(NoticeHistory, NoticeHistoryAdmin)
