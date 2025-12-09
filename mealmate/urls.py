from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = [
    path('', views.index, name='index'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.handle_login, name='login'),
    path('signup/submit/', views.handle_signup, name='handle_signup'),
    path('customer/<str:username>/', views.customer_home, name='customer_home'),
    path('restaurants/<int:restaurant_id>/menu/', views.restaurant_menu, name='restaurant_menu'),
    path('restaurants/<int:restaurant_id>/menu/customer/<str:username>/', views.customer_menu, name='customer_menu'),
    path('cart/<str:username>/', views.show_cart_page, name='show_cart_page'),
    path('cart/<int:item_id>/add/<str:username>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/<str:username>/', views.checkout, name='checkout'),
    path('orders/<str:username>/', views.orders, name='orders'),


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)