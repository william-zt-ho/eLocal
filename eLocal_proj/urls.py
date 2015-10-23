from django.conf.urls import patterns, include, url
from django.contrib import admin

from eLocal_app import views

urlpatterns = [
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^products', views.productpage),
    url(r'^shopping', views.shoppingPage),
    url(r'^store', views.storeSearchPage), #improve later to take into account store ID
    url(r'^add', views.addItemPage),
    url(r'^', views.homepage),
]
