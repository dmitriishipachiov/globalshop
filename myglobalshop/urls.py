"""
URL configuration for myglobalshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from myglobalshop import settings
from shop import views as shop_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='main')),
    path('shop/', include('shop.urls', namespace='shop')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('carts/', include('carts.urls', namespace='carts')),
    path('orders/', include('orders.urls', namespace='orders')),
    # Add direct access to products.json for compatibility with frontend JavaScript
    path('products/products.json', shop_views.ProductsJsonView.as_view(), name='products_json_root'),
    path('about/', include('about.urls', namespace='about')),
    path('legal/', include('legal.urls', namespace='legal')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
