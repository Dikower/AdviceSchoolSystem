from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
    # Main
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),

    # Content | protection and auth
    path('docs/', views.docs, name='docs'),
    path('panel/', views.panel, name='panel'),
    path('settings/', views.settings, name='settings'),

    # Auth
    path('reg/', views.func_reg, name='reg'),
    path('login/', views.func_login, name='login'),
    path('logout/', views.func_logout, name='logout'),
    path('change_password/', views.func_change_password, name='change_password'),
    path('recover_password/', views.func_recover_password, name='recover_password'),
    path('choose_person/', views.func_choose_person, name='choose_person'),
    path('set_person/', views.func_set_person, name='set_person'),

    # API
    path('api/docs/get_advice/', views.api_docs_get_advice, name='docs_get_advice'),
    path('api/docs/load_post_data/', views.api_load_post_data, name='load_post_data'),
    path('api/public/docs/get_advice/', views.api_public_docs_get_advice, name='docs_public_get_advice'),
]
