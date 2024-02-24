from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from strawberry.django.views import GraphQLView

from .schema import schema

urlpatterns = [
    path("", include("course.urls")),
    path("admin/", admin.site.urls),
    path("graphql", GraphQLView.as_view(graphiql=True, schema=schema)),
]

urlpatterns += staticfiles_urlpatterns()
