"""
URL configuration for new_authentication project.

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
from django.contrib.auth import views
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from alter_authentication.views import logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('alter_authentication.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', logout_view, name='logout'),  # используйте новое представление для выхода из системы
]