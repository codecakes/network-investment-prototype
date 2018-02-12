"""avicrypto URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^bank$', views.bank_website, name='bank_website'),

    url(r'^login$', views.app_login, name='app_login'),
    url(r'^signup', views.app_signup, name='app_signup'),
    url(r'^logout$', views.app_logout, name='app_logout'),
    url(r'^activate-account/(?P<token>.+)$', views.app_activate_account, name='app_activate_account'),
    url(r'^forgot-password', views.app_forgot_password, name='app_forgot_password'),
    url(r'^reset-password/(?P<token>.+)$', views.app_reset_password, name='app_reset_password'),

    url(r'^check-referal$', views.check_referal, name='check_referal'),
    url(r'^check-placement$', views.check_placement, name='check_placement'),

    url(r'^profile', views.profile, name='profile'),
    url(r'^home', views.home, name='dashboard'),
    url(r'^error$', views.error, name='error'),
    url(r'^network$', views.network, name='network'),

    url(r'^network/init/$', views.network_init, name='network_init'),
    url(r'^network/parent/$', views.network_parent, name='network_parent'),
    url(r'^network/children/(?P<user_id>.+)$', views.network_children, name='network_children'),

    url(r'^validate-user-transaction$', views.validate_user_transaction, name='validate_user_transaction'),
    url(r'^support$', views.support, name='support'),
    url(r'^uploads/simple/$', views.simple_upload, name='simple_upload'),
    url(r'^uploads/form/$', views.model_form_upload, name='model_form_upload'),
    url(r'^add/user/', views.add_user, name='profile'),
    url(r'^not-active', views.notactive, name="notactive"),
    url(r'^withdraw$', views.withdraw, name="withdraw"),

    # url(r'^add/user/(?P<id>[a-zA-Z0-9]{0,30})/$',views.add_user, name='add_user'),
    url(r'^404', views.app_404, name='app_404'),
]

handler404 = 'views.app_404'
