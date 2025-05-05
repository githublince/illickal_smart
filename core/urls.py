from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import agent_create

urlpatterns = [



    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),  # Assuming you have this view




    path('test-form/', views.test_agent_form),
    path('', views.home, name='core/home'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # Auth
    path('signup/manager/', views.signup_manager, name='signup_manager'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),

    # Manager actions
    path('manager/agent/<str:pk>/edit/', views.agent_update, name='agent_update'),
    path('manager/agent/<str:pk>/delete/', views.agent_delete, name='agent_delete'),
    path('manager/agent/<str:pk>/toggle/', views.agent_block_toggle, name='agent_block_toggle'),
    path('manager/agent/create/', views.agent_create, name='agent_create'),
    #path('manager/agent/<int:pk>/edit/', views.agent_update, name='agent_update'),
    #path('manager/agent/<int:pk>/delete/', views.agent_delete, name='agent_delete'),
    #path('manager/agent/<int:pk>/toggle/', views.agent_block_toggle, name='agent_block_toggle'),
    path('manager/transaction/create/', views.transaction_create, name='transaction_create'),
    
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/store/create/', views.store_create, name='store_create'),
    path('agent/bill/create/', views.create_bill, name='create_bill'),
    path('agent/bill/download/<str:billno>/', views.download_bill, name='download_bill'),

    # Manager URLs — Add similar routes for agent CRUD, transaction CRUD
]
