from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('menuitems/', views.menu_items),
    path('apiauth/', obtain_auth_token),
    path('manager/', views.manager),
    path('category/', views.category),
    path('catitems/', views.catitems),
    path('addmenu/', views.menupost),
    path('delivery/', views.delivery),
    path("itemstatus/", views.itemstatus),
    path("newcustomer/", views.newcustomer),
    path("addtocart/", views.addtocart),
    path('orderitem/', views.orderitem)




]