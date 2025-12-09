from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = [
    # Home and authentication paths
    path('', views.index, name='index'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.handle_login, name='login'),
    path('signup/submit/', views.handle_signup, name='handle_signup'),
    path('customer/<str:username>/', views.customer_home, name='customer_home'),

    # Restaurant-related paths
    path('restaurants/add', views.add_restaurant_page, name='add_restaurant_page'),
    path('restaurants/', views.show_restaurant_page, name='show_restaurant_page'),
    path('restaurants/add/', views.add_restaurant, name='add_restaurant'),
    path('restaurants/<int:restaurant_id>/menu/', views.restaurant_menu, name='restaurant_menu'),
    path('restaurants/<int:restaurant_id>/update/', views.update_restaurant, name='update_restaurant'),
    path('restaurants/<int:restaurant_id>/update/page/', views.update_restaurant_page, name='update_restaurant_page'),
    path('restaurants/<int:restaurant_id>/delete/', views.delete_restaurant, name='delete_restaurant'),

    path('menu/<int:menuItem_id>/update/', views.update_menuItem, name='update_menuItem'),
    path('menu/<int:menuItem_id>/update/page/', views.update_menuItem_page, name='update_menuItem_page'),
    path('menu/<int:menuItem_id>/delete/', views.delete_menuItem, name='delete_menuItem'),

    path('restaurants/<int:restaurant_id>/menu/customer/<str:username>/', views.customer_menu, name='customer_menu'),
    path('cart/<str:username>/', views.show_cart_page, name='show_cart_page'),
    path('cart/<int:item_id>/add/<str:username>/', views.add_to_cart, name='add_to_cart'),

    path('checkout/<str:username>/', views.checkout, name='checkout'),

    path('orders/<str:username>/', views.orders, name='orders'),


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)