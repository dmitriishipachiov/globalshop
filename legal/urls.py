from django.urls import path
from .views import PrivacyPolicyView, UserAgreementView, PersonalDataPolicyView

app_name = 'legal'

urlpatterns = [
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('user-agreement/', UserAgreementView.as_view(), name='user_agreement'),
    path('personal-data-policy/', PersonalDataPolicyView.as_view(), name='personal_data_policy'),
]
