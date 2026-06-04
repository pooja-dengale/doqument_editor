from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from editor.dtl_views import (
    login_view, signup_view, logout_view,
    editor_home, doc_new, doc_edit, doc_save, doc_import, doc_share, doc_revoke,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # REST API
    path('api/', include('editor.urls')),
    path('api/auth/token/', obtain_auth_token, name='obtain-token'),

    # Auth
    path('login/',  login_view,  name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),

    # Editor (login required)
    path('',              editor_home, name='editor-home'),
    path('new/',          doc_new,     name='doc-new'),
    path('import/',       doc_import,  name='doc-import'),
    path('doc/<int:doc_id>/',                       doc_edit,   name='doc-edit'),
    path('doc/<int:doc_id>/save/',                  doc_save,   name='doc-save'),
    path('doc/<int:doc_id>/share/',                 doc_share,  name='doc-share'),
    path('doc/<int:doc_id>/revoke/<str:username>/', doc_revoke, name='doc-revoke'),
]
