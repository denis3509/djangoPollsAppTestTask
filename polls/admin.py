from django.contrib import admin
from . import models as mdl
from . import service
from django.contrib import messages
from django.utils.translation import ngettext


# Register your models here.


class PollAdmin(admin.ModelAdmin):
    list_display = ["title", "published"]

    def has_change_permission(self, request, obj=None):

        if obj and obj.published:
            return False
        else:
            return True

    @admin.action(description="Mark selected as published")
    def make_published(self, request, queryset):
        updated = list()
        for poll in queryset:
            try:
                service.validate_poll(poll)
                poll.is_published = True
                poll.save()
                updated.append(poll)
            except:
                raise Exception("oops")

        self.message_user(
            request,
            ngettext(
                "%d poll was successfully marked as published.",
                "%d polls were successfully marked as published.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )


admin.site.register(mdl.Question)
admin.site.register(mdl.Choice)
admin.site.register(mdl.Poll, PollAdmin)
admin.site.register(mdl.UserTest)
