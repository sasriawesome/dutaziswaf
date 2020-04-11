from django.utils import translation
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
from django.conf import settings
from django.apps import apps

CASHFLOW_LIMIT_MUTATION_CHOICE = getattr(settings, 'CASHFLOW_LIMIT_MUTATION_CHOICE', [])

_ = translation.ugettext_lazy


def get_reference_limit_choice(**filter):
    if not CASHFLOW_LIMIT_MUTATION_CHOICE:
        return None

    if not isinstance(CASHFLOW_LIMIT_MUTATION_CHOICE, list):
        raise NotImplementedError(
            'CASHFLOW_LIMIT_MUTATION_CHOICE should be list object'
            ', item format should be app_label.model_name')

    app_list = []
    model_list = []
    for model in CASHFLOW_LIMIT_MUTATION_CHOICE:
        app_name, model_name = str(model).split('.')
        app_list.append(app_name)
        model_list.append(model_name)

    results = {
        'app_label__in': app_list,
        'model__in': model_list
    }
    results.update(**filter)
    return results


@deconstructible
class IDExistValidator:
    message = _('Ensure %(show_value)s) exist in %(limit_value)s.')
    code = 'inner_id_exist'

    def __init__(self, limit_value, message=None):
        self.limit_value = limit_value
        if message:
            self.message = message

    def __call__(self, value):
        cleaned = self.clean(value)
        limit_value = self.limit_value() if callable(self.limit_value) else self.limit_value

        models = []
        for item in limit_value:
            models.append(apps.get_model(item, require_ready=True))

        params = {
            'limit_value': ",".join([x._meta.verbose_name.title() for x in models]),
            'show_value': cleaned, 'value': value
        }
        self.limit_value = limit_value
        if self.id_not_in_db(cleaned, models):
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.limit_value == other.limit_value and
            self.message == other.message and
            self.code == other.code
        )

    def id_not_in_db(self, cleaned, models):
        try:
            for model in models:
                model.objects.get(pk=cleaned)
            return False
        except:
            return True

    def clean(self, x):
        return x
