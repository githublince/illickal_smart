# illickal_smart/urls.py

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup_manager/', views.signup_manager, name='signup_manager'),
    path('login/', views.login_view, name='login'),
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('agent/store/create/', views.store_create, name='store_create'),
    path('agent/bill/create/', views.create_bill, name='create_bill'),
    path('agent/bill/download/<str:billno>/', views.download_bill, name='download_bill'),
    path('manager/agent/create/', views.agent_create, name='agent_create'),
    path('manager/agent/update/<str:pk>/', views.agent_update, name='agent_update'),
    path('manager/agent/delete/<str:pk>/', views.agent_delete, name='agent_delete'),
    path('manager/agent/block/<str:pk>/', views.agent_block_toggle, name='agent_block_toggle'),
    path('manager/transaction/create/', views.transaction_create, name='transaction_create'),
    path('manager/manager-agent-transaction/create/', views.manager_agent_transaction_create, name='manager_agent_transaction_create'),
    path('manager/manager-agent-transaction/list/', views.manager_agent_transaction_list, name='manager_agent_transaction_list'),
    path('manager/products/create/', views.product_create, name='product_create'),
    path('manager/products/search/', views.product_search, name='product_search'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)