import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone, translation

_ = translation.ugettext_lazy


class BaseManager(models.Manager):
    """
        Implement paranoid mechanism queryset
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def get(self, *args, **kwargs):
        kwargs['is_deleted'] = False
        return super().get(*args, **kwargs)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    objects = BaseManager()

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='uuid')
    is_deleted = models.BooleanField(
        default=False,
        editable=False,
        verbose_name=_('is deleted?'))
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        null=True, blank=True,
        related_name="%(class)s_deleter",
        on_delete=models.CASCADE,
        verbose_name=_('deleter'))
    deleted_at = models.DateTimeField(
        null=True, blank=True, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        null=True, blank=True,
        related_name="%(class)s_creator",
        on_delete=models.CASCADE,
        verbose_name=_('creator'))
    created_at = models.DateTimeField(
        default=timezone.now, editable=False)
    modified_at = models.DateTimeField(
        null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        self.modified_at = timezone.now()
        super().save(**kwargs)

    def delete(self, using=None, keep_parents=False, paranoid=False):
        """
            Give paranoid delete mechanism to each record
        """
        if paranoid:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)
