from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.static import serve 


urlpatterns = [ 
    path('contact_view/',views.contact_view, name='contact_view'),
    path('contacts_view/',views.contacts_view,name='contacts_view'),
    path('submit-comment/', views.submit_comment, name='submit_comment'),
    path('send-message/', views.send_message, name='send_message'),
    path('book/',views.book_views,name="book"),
    path('select_room/', views.select_room, name='select_room'),
    path('select/', views.select, name='select'),
    path('book-now/', views.book_now, name='book_now'),
    path('complete_booking/', views.complete_booking, name='complete_booking'),
    path('booking_confirm/', views.booking_confirm, name='booking_confirm'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('booking-success/<int:booking_id>/', views.booking_success, name='booking_success'),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



 

