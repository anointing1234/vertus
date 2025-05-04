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
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



 

