"""
DTL views — full session authentication.
Login, signup, logout + all document CRUD views protected by @login_required.
"""
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Document, DocumentShare


# ─────────────────────────────────────────────────────────────────────────────
# Auth views
# ─────────────────────────────────────────────────────────────────────────────

def login_view(request):
    """Login page — redirects to home if already authenticated."""
    if request.user.is_authenticated:
        return redirect('editor-home')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', 'editor-home'))
        else:
            error = 'Invalid username or password. Please try again.'

    return render(request, 'editor/login.html', {'error': error})


def signup_view(request):
    """Sign up page — creates account and logs in immediately."""
    if request.user.is_authenticated:
        return redirect('editor-home')

    errors = {}
    values = {}

    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        values = {'username': username, 'email': email}

        # Validate
        if not username:
            errors['username'] = 'Username is required.'
        elif len(username) < 3:
            errors['username'] = 'Username must be at least 3 characters.'
        elif User.objects.filter(username__iexact=username).exists():
            errors['username'] = 'That username is already taken.'

        if not password1:
            errors['password1'] = 'Password is required.'
        elif len(password1) < 6:
            errors['password1'] = 'Password must be at least 6 characters.'
        elif password1 != password2:
            errors['password2'] = 'Passwords do not match.'

        if not errors:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
            )
            login(request, user)
            return redirect('editor-home')

    return render(request, 'editor/signup.html', {'errors': errors, 'values': values})


@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    return redirect('login')


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_sidebar_docs(user):
    my_docs = Document.objects.filter(owner=user).order_by('-updated_at')

    shared_qs = (
        Document.objects
        .filter(shares__shared_with=user)
        .exclude(owner=user)
        .distinct()
        .order_by('-updated_at')
    )
    shared_docs = []
    for doc in shared_qs:
        share = doc.shares.filter(shared_with=user).first()
        doc.my_permission = share.permission if share else 'view'
        shared_docs.append(doc)

    return my_docs, shared_docs


def _build_context(request, active_doc=None, save_status=None, open_share_modal=False):
    user = request.user
    my_docs, shared_docs = _get_sidebar_docs(user)

    can_edit = False
    is_owner = False

    if active_doc:
        is_owner = active_doc.owner == user
        if is_owner:
            can_edit = True
        else:
            share = active_doc.shares.filter(shared_with=user).first()
            can_edit = bool(share and share.permission == 'edit')

        shared_usernames = list(
            active_doc.shares.values_list('shared_with__username', flat=True)
        )
        shared_usernames.append(active_doc.owner.username)
        shareable_users = User.objects.exclude(username__in=shared_usernames)
    else:
        shareable_users = User.objects.none()

    return {
        'my_docs':          my_docs,
        'shared_docs':      shared_docs,
        'active_doc':       active_doc,
        'can_edit':         can_edit,
        'is_owner':         is_owner,
        'shareable_users':  shareable_users,
        'save_status':      save_status,
        'open_share_modal': open_share_modal,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Editor views  (all require login)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def editor_home(request):
    ctx = _build_context(request)
    return render(request, 'editor/editor.html', ctx)


@login_required
def doc_new(request):
    doc = Document.objects.create(
        title='Untitled Document', content='', owner=request.user
    )
    return redirect('doc-edit', doc_id=doc.id)


@login_required
def doc_edit(request, doc_id):
    doc = get_object_or_404(
        Document.objects.filter(
            Q(owner=request.user) | Q(shares__shared_with=request.user)
        ).distinct(),
        pk=doc_id,
    )
    ctx = _build_context(request, active_doc=doc)
    return render(request, 'editor/editor.html', ctx)


@login_required
@require_http_methods(['POST'])
def doc_save(request, doc_id):
    doc = get_object_or_404(
        Document.objects.filter(
            Q(owner=request.user) | Q(shares__shared_with=request.user)
        ).distinct(),
        pk=doc_id,
    )

    # Permission check
    if doc.owner != request.user:
        share = doc.shares.filter(shared_with=request.user).first()
        if not share or share.permission != 'edit':
            ctx = _build_context(request, active_doc=doc, save_status='error')
            return render(request, 'editor/editor.html', ctx, status=403)

    doc.title   = request.POST.get('title', doc.title).strip() or 'Untitled Document'
    doc.content = request.POST.get('content', doc.content)
    doc.save()

    ctx = _build_context(request, active_doc=doc, save_status='saved')
    return render(request, 'editor/editor.html', ctx)


@login_required
@require_http_methods(['POST'])
def doc_import(request):
    title   = request.POST.get('title', 'Imported Document').strip() or 'Imported Document'
    content = request.POST.get('content', '')
    doc = Document.objects.create(title=title, content=content, owner=request.user)
    return redirect('doc-edit', doc_id=doc.id)


@login_required
@require_http_methods(['POST'])
def doc_share(request, doc_id):
    doc = get_object_or_404(Document, pk=doc_id, owner=request.user)
    username   = request.POST.get('username', '').strip()
    permission = request.POST.get('permission', 'view')

    if username and permission in ('view', 'edit'):
        try:
            target = User.objects.get(username=username)
            if target != request.user:
                DocumentShare.objects.update_or_create(
                    document=doc,
                    shared_with=target,
                    defaults={'permission': permission},
                )
        except User.DoesNotExist:
            pass

    ctx = _build_context(request, active_doc=doc, open_share_modal=True)
    return render(request, 'editor/editor.html', ctx)


@login_required
@require_http_methods(['POST'])
def doc_revoke(request, doc_id, username):
    doc = get_object_or_404(Document, pk=doc_id, owner=request.user)
    DocumentShare.objects.filter(
        document=doc, shared_with__username=username
    ).delete()
    ctx = _build_context(request, active_doc=doc, open_share_modal=True)
    return render(request, 'editor/editor.html', ctx)
