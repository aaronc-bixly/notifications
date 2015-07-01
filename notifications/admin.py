from django.contrib import admin

from notifications.models import NoticeType, NoticeQueueBatch, NoticeSetting, NoticeHistory


class NoticeHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ["notice_type", "recipient", "sender", "extra_context", "sent_at"]


class NoticeTypeAdmin(admin.ModelAdmin):
    list_display = ["label", "display", "description", "default"]


class NoticeSettingAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "notice_type", "medium", "scoping", "send"]


admin.site.register(NoticeQueueBatch)
admin.site.register(NoticeType, NoticeTypeAdmin)
admin.site.register(NoticeSetting, NoticeSettingAdmin)
admin.site.register(NoticeHistory, NoticeHistoryAdmin)
