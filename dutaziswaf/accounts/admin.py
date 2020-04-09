from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.shortcuts import reverse
from .models import User

from django_extra_referrals.models import Referral


class AdminBase(admin.ModelAdmin):
    inspect_template = None

    def get_urls(self):
        from django.urls import path
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super().get_urls()
        extra_urls = [
            path('<path:object_id>/inspect/',
                 self.admin_site.admin_view(self.inspect_view),
                 name='%s_%s_inspect' % info
                 )
        ]
        return extra_urls + urls

    def inspect_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        opts = self.model._meta
        if not self.has_view_or_change_permission(request, obj):
            return PermissionError("You don't have any permissions")
        context = {
            **self.admin_site.each_context(request),
            'self': self,
            'opts': opts,
            'instance': obj,
            **(extra_context or {})
        }

        return TemplateResponse(request, self.inspect_template or [
            'admin/%s/%s/inspect.html' % (opts.app_label, opts.model_name),
            'admin/%s/inspect.html' % opts.app_label,
            'admin/inspect.html'
        ], context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        if self.has_change_permission(request, obj):
            return self.changeform_view(request, object_id, form_url, extra_context)
        return self.inspect_view(request, object_id, extra_context)


class ReferralInline(admin.TabularInline):
    model = Referral
    can_delete = False
    extra = 1
    max_num = 1


@admin.register(User)
class CustomUserAdmin(UserAdmin, AdminBase):
    ordering = ('username',)
    search_fields = ('username', 'email')
    list_display = ('username', 'email', 'get_full_name','is_muzakki', 'is_mustahiq', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_muzakki', 'is_mustahiq', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_mustahiq',
                'is_muzakki',
                'is_staff',
                'groups',
                'user_permissions'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = [ReferralInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('referral')

    def user_name(self, obj):
        admin_url = reverse('admin:dutaziswaf_accounts_user_inspect', args=(obj.id,))
        return format_html('<a href="%s">%s</a>' % (admin_url, obj.username))
