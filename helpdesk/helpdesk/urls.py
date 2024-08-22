"""
URL configuration for helpdesk project.

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
from django.urls import path
from support import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', views.Index_function , name="Index_function") ,
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login'),
    
    
#Admin_panel 
#-----------------------------------------------------------------------------------------------------------------------------
    
    path('admin-home/', views.admin_home, name='admin_home'),
    path('profile-updates2/', views.profile_updates_admin, name='profile_updates_admin'),
    path('manage-tickets/', views.manage_tickets_ad, name='manage_tickets_ad'),
    path('update-ticket/<int:ticket_id>/', views.update_ticket_admin, name='update_ticket_admin'),
    path('view-ticket/<int:ticket_id>/', views.view_ticket_admin, name='view_ticket_admin'),
    
    
    
    
    
#staff_panel 
#-----------------------------------------------------------------------------------------------------------------------------

    path('staff-home/', views.staff_home, name='staff_home'),
    path('profile-updates/', views.profile_updates, name='profile_updates'),
    path('create-ticket/', views.create_ticket, name='create_ticket'),
    path('manage-tickets1/', views.manage_tickets, name='manage_tickets'),
    path('update-ticket1/<int:ticket_id>/', views.update_ticket, name='update_ticket'),
    path('delete-note/<int:note_id>/', views.delete_note, name='delete_note'),
    path('view-ticket1/<int:ticket_id>/', views.view_ticket, name='view_ticket'),
    
    
    
    
    
#customer_panel 
#-----------------------------------------------------------------------------------------------------------------------------

    path('customer-home/', views.customer_home, name='customer_home'),
    path('profile-updates1/', views.profile_updates_customer, name='profile_updates_customer'),
    path('customer_tickets/', views.customer_ticket_list, name='customer_ticket_list'),
    path('customer_tickets/<int:ticket_id>/', views.customer_ticket_detail, name='customer_ticket_detail'),
    
    
    path('logout/', views.logout_view, name='logout'),
    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)