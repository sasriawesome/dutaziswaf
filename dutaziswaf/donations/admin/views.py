from django.db import models
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import redirect

from wagtail.contrib.modeladmin.views import InstanceSpecificView, FormView, DeleteView
from wagtail.admin.messages import messages


class ConfirmView(InstanceSpecificView):
    page_title = _('Confirm')

    def check_action_permitted(self, user):
        return self.permission_helper.user_can_confirm_obj(user, self.instance)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not self.check_action_permitted(request.user):
            raise PermissionDenied
        if self.is_pagemodel:
            return redirect(
                self.url_helper.get_action_url('confirm', self.pk_quoted)
            )
        return super().dispatch(request, *args, **kwargs)

    def get_meta_title(self):
        return _('Confirm %s and update related balance.') % self.verbose_name

    def confirmation_message(self):
        return _(
            "Are you sure you want to confirm this %s? If other things in your "
            "site are related to it, they may also be affected."
        ) % self.verbose_name

    def confirm_instance(self):
        self.instance.confirm(self.request)

    def post(self, request, *args, **kwargs):
        if self.request.POST.get('inner_id') != self.instance.inner_id:
            context = self.get_context_data(
                password_error=True,
                inner_id=request.POST.get('inner_id')
            )
            return self.render_to_response(context)

        try:
            msg = _("%(model_name)s '%(instance)s' confirmed.") % {
                'model_name': self.verbose_name,
                'instance': self.instance
            }
            self.confirm_instance()
            messages.success(request, msg)
            return redirect(self.index_url)
        except Exception as err:
            context = self.get_context_data(
                confirmation_error=True,
            )
            return self.render_to_response(context)

    def get_template_names(self):
        return (
            self.template_name
            or self.model_admin.get_templates('confirm')
        )


class CancelView(InstanceSpecificView):
    page_title = _('Cancel')

    def check_action_permitted(self, user):
        return self.permission_helper.user_can_cancel_obj(user, self.instance)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not self.check_action_permitted(request.user):
            raise PermissionDenied
        if self.is_pagemodel:
            return redirect(
                self.url_helper.get_action_url('cancel', self.pk_quoted)
            )
        return super().dispatch(request, *args, **kwargs)

    def get_meta_title(self):
        return _('Cancel %s and update related balance.') % self.verbose_name

    def cancellation_message(self):
        return _(
            "Are you sure you want to cancel this %s? If other things in your "
            "site are related to it, they may also be affected."
        ) % self.verbose_name

    def cancel_instance(self):
        self.instance.cancel(self.request)

    def post(self, request, *args, **kwargs):
        if request.POST.get('inner_id') != self.instance.inner_id:
            context = self.get_context_data(
                password_error=True,
                inner_id=request.POST.get('inner_id')
            )
            return self.render_to_response(context)
        try:
            msg = _("%(model_name)s '%(instance)s' cancelled.") % {
                'model_name': self.verbose_name,
                'instance': self.instance
            }
            self.cancel_instance()
            messages.success(request, msg)
            return redirect(self.index_url)
        except Exception as err:
            context = self.get_context_data(
                cancellation_error=True,
            )
            return self.render_to_response(context)

    def get_template_names(self):
        return (
            self.template_name
            or self.model_admin.get_templates('cancel')
        )
