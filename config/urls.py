"""Routes principales du projet PubliEPT."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("django-admin/", admin.site.urls),
    path("", include("publiept.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "publiept.views.page_404"
handler403 = "publiept.views.page_403"

admin.site.site_header = "PubliEPT — Administration technique"
admin.site.site_title = "PubliEPT"
admin.site.index_title = "Base de données de la plateforme"
