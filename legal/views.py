from django.views.generic import TemplateView, DetailView
from django.shortcuts import get_object_or_404
from .models import UserAgreement, PrivacyPolicy, PersonalDataPolicy

class PrivacyPolicyView(DetailView):
    model = PrivacyPolicy
    template_name = 'legal/privacy_policy.html'
    context_object_name = 'policy'

    def get_object(self):
        return get_object_or_404(PrivacyPolicy, is_active=True)

class UserAgreementView(DetailView):
    model = UserAgreement
    template_name = 'legal/user_agreement.html'
    context_object_name = 'agreement'

    def get_object(self):
        return get_object_or_404(UserAgreement, is_active=True)

class PersonalDataPolicyView(DetailView):
    model = PersonalDataPolicy
    template_name = 'legal/personal_data_policy.html'
    context_object_name = 'policy'

    def get_object(self):
        return get_object_or_404(PersonalDataPolicy, is_active=True)
