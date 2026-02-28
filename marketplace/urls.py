from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.listings.urls')),
    path('api/auth/', include('apps.users.urls')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/panel/', include('apps.panel.urls')),
    # Все остальные маршруты — SPA
    path('admin-panel/', TemplateView.as_view(template_name='admin_panel.html'), name='admin-panel'),
    path('', TemplateView.as_view(template_name='index.html')),
    path('<path:path>', TemplateView.as_view(template_name='index.html')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
