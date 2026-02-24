from django.urls import path
from .views import PageContentAboutView, PageContentContactsView

app_name = 'about'

urlpatterns = [
    path('', PageContentAboutView.as_view(), {'page_type': 'about'}, name='about'),
    path('contacts/', PageContentContactsView.as_view(), {'page_type': 'contacts'}, name='contacts'),
]
