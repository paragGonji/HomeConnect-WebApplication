from django.contrib import admin
from django.urls import path
from kitchen import views as kitchen_views  # Import kitchen views with an alias
from home.views import *  # Assuming views from the home app
from delivery import views as delivery_views  # Import delivery views with an alias # Assuming views from the vege app
from vege import views as vege_views  # Import views from vege app

from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    # Home app URLs
    path('', home, name="Home"),
    path('homeconnect/', vege_views.homeconnect, name="homeconnect"),
    path('popular/', vege_views.popular, name="popular"),
    path('order/', vege_views.order, name='order'),  # Add this line
    path('cart/', vege_views.cart, name="cart"),
    path('add_to_cart/', vege_views.add_to_cart, name="add_to_cart"),
    path('update_quantity/<int:item_id>/', vege_views.update_quantity, name='update_quantity'),
    path('delete_item/<int:item_id>/', vege_views.delete_item, name='delete_item'),
    path('save_user_details/', vege_views.save_user_details, name="save_user_details"),
    path('verify-payment/', vege_views.verify_payment, name='verify_payment'),
    path('receipe_suggestion/', vege_views.receipe_suggestion, name='receipe_suggestion'),




    path('receipes/', vege_views.receipes, name="receipes"),
    path('login/', vege_views.login_page, name="login_page"),
    path('logout/', vege_views.logout_page, name="logout_page"),
    path('register/', vege_views.register, name="register"),
    path('api/receive_order/', vege_views.receive_order, name='receive_order'),
    path('vege/api/receive_order/', vege_views.receive_order, name='receive_order'),


    
    #home
    path('about/', about, name="about"),
    path('contact/', contact, name="contact"),
    path('second-page/', second_page, name="second_page"),



    # Kitchen app URLs
    path('kitchen-login/', kitchen_views.kitchen_login, name="kitchen_login"),
    path('kitchen-register/', kitchen_views.kitchen_register, name="kitchen_register"),
    path('personal-kitchen/', kitchen_views.personal_kitchen, name="personal_kitchen"),
    path('activate/<uidb64>/<token>/', kitchen_views.activate, name='activate'),
    path('menu/', kitchen_views.kitchen_menu, name='kitchen_menu'),
    path('menu/add/', kitchen_views.add_dish, name='add_dish'),
    path('menu/update/', kitchen_views.update_dish, name='update_dish'),  
    path('menu/delete/<int:dish_id>/', kitchen_views.delete_dish, name='delete_dish'),
    path('menu/toggle-availability/', kitchen_views.toggle_availability, name='toggle_availability'),
    path('kitchen-earning/', kitchen_views.kitchen_earning, name="kitchen_earning"),
    path('reset_kitchenearnings/', kitchen_views.reset_kitchenearnings, name="reset_kitchenearnings"),


    # Delivery app URLs
    path('delivery-login/', delivery_views.delivery_login, name="delivery_login"),
    path('delivery-register/', delivery_views.delivery_register, name="delivery_register"),
    path('delivery-activate/<uidb64>/<token>/', delivery_views.activate_delivery, name='activate_delivery'),
    path('delivery-person/', delivery_views.delivery_person, name="delivery_person"),
    path('delivery-dashboard/', delivery_views.delivery_dashboard, name="delivery_dashboard"),  # ✅ Add this line
    path('delivery_earning/', delivery_views.delivery_earning, name="delivery_earning"),

    path('delivery_order/', delivery_views.delivery_order, name="delivery_order"),
    path('delivery-location/', delivery_views.delivery_location, name="delivery_location"),
    path('delivered_order/', delivery_views.delivered_order, name="delivered_order"),
    path('reset-earnings/', delivery_views.reset_earnings, name='reset_earnings'),


    # Admin URL
    path('admin/', admin.site.urls),
]

# Media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()

