from django.urls import path
from .import views 

urlpatterns = [
    path('',views.index,name='index'),
    path('python/',views.python,name='python'),
    path('java/',views.java,name='java'),
    path('php/',views.php,name='php'),
    path('contact/',views.contact,name='contact'),
    path('login/',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('send_otp/',views.send_otp,name='send_otp'),
    path('logout/',views.logout,name='logout'),
    path('enter_email/',views.enter_email,name='enter_email'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('change_password/',views.change_password,name='change_password'),
    path('add_book/',views.add_book,name='add_book'),
    path('seller_index/',views.seller_index,name='seller_index'),
    path('view_book/',views.view_book,name='view_book'),
    path('book_detail/<int:pk>/',views.book_detail,name='book_detail'),
    path('delete_book/<int:pk>/',views.delete_book,name='delete_book'),
    path('inactive_book/',views.inactive_book,name='inactive_book'),
    path('active_book/<int:pk>/',views.active_book,name='active_book'),
    path('search_book/',views.search_book,name='search_book'),
    path('profile/',views.profile,name='profile'),
    path('user_book_details/<int:pk>/',views.user_book_details,name='user_book_details'),
    path('add_to_cart/<int:pk>/',views.add_to_cart,name='add_to_cart'),
    path('my_cart/',views.my_cart,name='my_cart'),
    path('remove_cart/<int:pk>/',views.remove_cart,name='remove_cart'),
    path('move_to_wishlist/<int:pk>/',views.move_to_wishlist,name='move_to_wishlist'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('remove_wishlist/<int:pk>/',views.remove_wishlist,name='remove_wishlist'),
    path('move_to_cart/<int:pk>/',views.move_to_cart,name='move_to_cart'),
    path('add_to_wishlist/<int:pk>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('pay/',views.initiate_payment, name='pay'),
    path('callback/',views.callback, name='callback'),



]
