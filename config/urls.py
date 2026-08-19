from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve

admin.site.site_header = 'UZNR administracija'
admin.site.site_title = 'UZNR admin'
admin.site.index_title = 'Upravljanje sadržajem'
# Adds the orientation panel above the model list on the admin home page.
admin.site.index_template = 'admin/uznr_index.html'
# Replaces Django's bare sign-in box with the branded single-card layout.
admin.site.login_template = 'admin/uznr_login.html'
# "Pogledaj sajt" in the header. Django defaults this to '/', which on this
# project is the API server's own root -- it serves only admin/, api/ and
# media/, so the link 404'd. The public site lives somewhere else entirely,
# which is exactly what SITE_URL already records.
admin.site.site_url = settings.SITE_URL


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('content.urls')),
    path('api/health', lambda request: JsonResponse({'status': 'ok'})),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
