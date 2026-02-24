from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.ShopListView.as_view(), name='shop'),
    path("category/<slug:category_slug>/", views.CategoryListView.as_view(), name='category'),
    path('detail/<slug:product_slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('favorite/<slug:product_slug>/', views.FavoriteToggleView.as_view(), name='favorite_toggle'),
    path('favorites/', views.FavoriteListView.as_view(), name='favorites'),
    path('api/favorites/count/', views.FavoriteCountView.as_view(), name='favorites_count'),
    path('products/products.json', views.ProductsJsonView.as_view(), name='products_json'),
]
