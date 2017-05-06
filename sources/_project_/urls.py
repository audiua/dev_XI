"""_project_ URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from voting import views

router = routers.DefaultRouter()
router.register(r'counsils', views.CounsilViewSet)
router.register(r'counsil-sessions', views.CounsilSessionViewSet)
router.register(r'deputies', views.DeputyViewSet)
router.register(r'laws', views.LawViewSet)
router.register(r'law-votings', views.LawVotingViewSet)



schema_view = get_swagger_view(title='Voting API')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/(?P<version>(v1|v2))/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^$', schema_view)
]
