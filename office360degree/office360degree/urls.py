"""
URL configuration for office360degree project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import include, path
from .views import index, about, clients, booking, knowledgebase, contact, epaper, ad_list, ad_detail, book_ad, payment_success
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    path('about', about, name='about'),
    path('clients', clients, name='clients'),
    path('booking', booking, name='booking'),
    path('epaper', epaper, name='epaper'),
    path('knowledgebase', knowledgebase, name='knowledgebase'),
    path('contact', contact, name='contact'),
    path('admin/', admin.site.urls),
    path('owner/', include('owner.urls')),
    path('ads/', ad_list, name='ad_list'),
    path('ads/book/<int:ad_id>/', book_ad, name='book_ad'),
    path('ads/<int:ad_id>/', ad_detail, name='ad_detail'),
    path('payment/success/<int:booking_id>/', payment_success, name='complete_payment'),
]

admin.site.site_header = "Market Movers Plus Admin"
admin.site.site_title = "Market Movers Plus Admin"
admin.site.index_title = "Welcome Market Movers Plus Admin"

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)