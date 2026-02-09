"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [

    path ('',views.home,name='home'),
    path('login/',views.login,name='login'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('police_registration/',views.police_registration,name='police_registration'),
    path('user_registration/',views.user_registration,name='user_registration'),

    # ------------------------------------------ ADMIN ------------------------------------------------------------------------------------

    path('admin_home/',views.admin_home,name='admin_home'),

    path('admin_verify_police/',views.admin_verify_police,name='admin_verify_police'),
    path('admin_approve_police/<int:id>/', views.admin_approve_police, name='admin_approve_police'),
    path('admin_reject_police/<int:id>/',views.admin_reject_police,name='admin_reject_police'),
    path('admin_view_missing_data/<int:id>/', views.admin_view_missing_data, name='admin_view_missing_data'),
    path('admin_manage_awareness/',views.admin_manage_awareness,name='admin_manage_awareness'),
    path('admin_update_awareness/<int:id>/', views.admin_update_awareness, name='admin_update_awareness'),
    path('admin_delete_awareness/<int:id>/',views.admin_delete_awareness,name='admin_delete_awareness'),

    path('admin_view_complaints/',views.admin_view_complaints,name='admin_view_complaints'),


    # ------------------------------------------ AUTHORITY ------------------------------------------------------------------------------------

    path('police_home/',views.police_home,name='police_home'),
    path('police_view_case_report/',views.police_view_case_report,name='police_view_case_report'),
    path("police_view_user/<int:case_id>/", views.police_view_user, name="police_view_user"),
    path("police_accept_report/<int:case_id>/", views.police_accept_report, name="police_accept_report"),
    path("police_reject_report/<int:case_id>/", views.police_reject_report, name="police_reject_report"),
    path("police_update_status/<int:case_id>/", views.police_update_status, name="police_update_status"),




    path('police_view_public_report/',views.police_view_public_report,name='police_view_public_report'),

   
    # ------------------------------------------ USER ------------------------------------------------------------------------------------

    path('user_home/', views.user_home, name='user_home'),
    path("user_profile/", views.user_profile, name="user_profile"),
    path("user_submit_case/", views.submit_case, name="submit_case"),
    path("user_view_case_progress/", views.view_case_progress, name="view_case_progress"),
    path("user_view_awareness/", views.user_view_awareness, name="user_view_awareness"),
    path("user_complaint/", views.user_complaint, name="user_complaint"),
    path("predict_child/", views.predict_child, name="predict_child"),



]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)