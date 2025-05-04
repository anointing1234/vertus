from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.static import serve 


urlpatterns = [ 
    path('',views.home_view,name='home'),
    path('about/',views.about_view,name='about'),
    path('faq/',views.faq_view,name='faq'),
    path('pricing/',views.pricing_view,name='pricing'),
    path('room/<int:id>/',views.room_detail_view,name='room_details'),
    path('rooms/',views.rooms_view,name='rooms'),
    path('services/',views.services_view,name='services'),
    path('contact/',views.contact_view,name='contact'),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



 

