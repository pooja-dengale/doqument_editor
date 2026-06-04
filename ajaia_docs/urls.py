from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from editor.dtl_views import (
    switch_user,
    editor_home, doc_new, doc_edit, doc_save, doc_import, doc_share, doc_revoke,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # REST API (kept for tests)
    path('api/', include('editor.urls')),
    path('api/auth/token/', obtain_auth_token, name='obtain-token'),

    # DTL views — no login required
    path('',              editor_home, name='editor-home'),
    path('switch-user/',  switch_user, name='switch-user'),
    path('new/',          doc_new,     name='doc-new'),
    path('import/',       doc_import,  name='doc-import'),
    path('doc/<int:doc_id>/',                          doc_edit,   name='doc-edit'),
    path('doc/<int:doc_id>/save/',                     doc_save,   name='doc-save'),
    path('doc/<int:doc_id>/share/',                    doc_share,  name='doc-share'),
    path('doc/<int:doc_id>/revoke/<str:username>/',    doc_revoke, name='doc-revoke'),
]
