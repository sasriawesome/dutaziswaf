from django.db.utils import cached_property
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.utils import quote
from wagtail.contrib.modeladmin.helpers import ButtonHelper, AdminURLHelper, PermissionHelper


class ReadOnlyPermissionHelper(PermissionHelper):
    def user_can_edit_obj(self, user, obj):
        return False

    def user_can_create(self, user):
        return False

    def user_can_delete_obj(self, user, obj):
        return False


class ConfirmCancelPermissionHelper(PermissionHelper):
    """
     Add extra permissions method that return a boolean to indicate whether
     `user` is permitted to 'confirm' and 'cancel' a specific `self.model` instance.
    """

    def user_can_confirm_obj(self, user, obj):
        perm_codename = self.get_perm_codename('confirm')
        return self.user_has_specific_permission(user, perm_codename)

    def user_can_cancel_obj(self, user, obj):
        perm_codename = self.get_perm_codename('cancel')
        return self.user_has_specific_permission(user, perm_codename)


class ConfirmCancelURLHelper(AdminURLHelper):
    @cached_property
    def confirm_url(self):
        return self.get_action_url('confirm')

    @cached_property
    def cancel_url(self):
        return self.get_action_url('cancel')


class ConfirmCancelButtonHelper(ButtonHelper):
    confirm_button_classnames = []
    cancel_button_classnames = []

    def confirm_button(self, pk, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.confirm_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': self.url_helper.get_action_url('confirm', quote(pk)),
            'label': _('Confirm'),
            'classname': cn,
            'title': _('Confirm this %s') % self.verbose_name,
        }

    def cancel_button(self, pk, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.cancel_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': self.url_helper.get_action_url('cancel', quote(pk)),
            'label': _('Cancel'),
            'classname': cn,
            'title': _('Cancel this %s') % self.verbose_name,
        }

    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None,
                            classnames_exclude=None):

        if exclude is None:
            exclude = []
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        ph = self.permission_helper
        usr = self.request.user
        pk = getattr(obj, self.opts.pk.attname)

        btns = super().get_buttons_for_obj(
            obj, exclude, classnames_add, classnames_exclude
        )

        if ('confirm' not in exclude and ph.user_can_confirm_obj(usr, obj)):
            btns.append(
                self.confirm_button(pk, classnames_add, classnames_exclude)
            )
        if ('cancel' not in exclude and ph.user_can_cancel_obj(usr, obj)):
            btns.append(
                self.cancel_button(pk, classnames_add, classnames_exclude)
            )
        return btns


class DonationPermissionHelper(ConfirmCancelPermissionHelper, PermissionHelper):
    def user_can_edit_obj(self, user, obj):
        if obj:
            if obj.is_cancelled or obj.is_paid:
                return False
        return super().user_can_edit_obj(user, obj)

    def user_can_delete_obj(self, user, obj):
        return False

    def user_can_cancel_obj(self, user, obj):
        if obj:
            if not obj.is_paid or obj.is_cancelled:
                return False
        return super().user_can_cancel_obj(user, obj)

    def user_can_confirm_obj(self, user, obj):
        if obj:
            if obj.is_paid:
                return False
        return super().user_can_confirm_obj(user, obj)


class WithdrawPermissionHelper(ConfirmCancelPermissionHelper, PermissionHelper):
    def user_can_edit_obj(self, user, obj):
        if obj:
            if obj.is_cancelled or obj.is_paid:
                return False
        return super().user_can_edit_obj(user, obj)

    def user_can_delete_obj(self, user, obj):
        return False

    def user_can_cancel_obj(self, user, obj):
        if obj:
            if not obj.is_paid or obj.is_cancelled:
                return False
        return super().user_can_cancel_obj(user, obj)

    def user_can_confirm_obj(self, user, obj):
        if obj:
            if obj.is_paid:
                return False
        return super().user_can_confirm_obj(user, obj)