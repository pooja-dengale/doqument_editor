"""
DTL views — no authentication required.
Active user is stored in the session as a simple username string.
Anyone can switch between Alice, Bob, and Charlie via the header dropdown.
"""
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Document, DocumentShare

USERS = ['alice', 'bob', 'charlie']


# ── Active-user helper ────────────────────────────────────────────────────────

def _get_active_user(request):
    """Return the User object for the current session's active_user."""
    username = request.session.get('active_user', USERS[0])
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        # Fallback to first seeded user
        return User.objects.filter(username__in=USERS).first()


# ── Switch user (POST from header dropdown) ───────────────────────────────────

@require_http_methods(['POST'])
def switch_user(request):
    username = request.POST.get('active_user', USERS[0])
    if username in USERS:
        request.session['active_user'] = username
    # Redirect back to wherever the user was
    return redirect(request.POST.get('next', '/'))


# ── Sidebar helpers ───────────────────────────────────────────────────────────

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
    user = _get_active_user(request)
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
        shareable_users = User.objects.filter(username__in=USERS).exclude(
            username__in=shared_usernames
        )
    else:
        shareable_users = User.objects.none()

    return {
        'active_user':      user,
        'all_users':        USERS,
        'my_docs':          my_docs,
        'shared_docs':      shared_docs,
        'active_doc':       active_doc,
        'can_edit':         can_edit,
        'is_owner':         is_owner,
        'shareable_users':  shareable_users,
        'save_status':      save_status,
        'open_share_modal': open_share_modal,
    }


# ── Views ─────────────────────────────────────────────────────────────────────

def editor_home(request):
    ctx = _build_context(request)
    return render(request, 'editor/editor.html', ctx)


def doc_new(request):
    user = _get_active_user(request)
    doc = Document.objects.create(title='Untitled Document', content='', owner=user)
    return redirect('doc-edit', doc_id=doc.id)


def doc_edit(request, doc_id):
    user = _get_active_user(request)
    doc = get_object_or_404(
        Document.objects.filter(
            Q(owner=user) | Q(shares__shared_with=user)
        ).distinct(),
        pk=doc_id,
    )
    ctx = _build_context(request, active_doc=doc)
    return render(request, 'editor/editor.html', ctx)


@require_http_methods(['POST'])
def doc_save(request, doc_id):
    user = _get_active_user(request)
    doc = get_object_or_404(
        Document.objects.filter(
            Q(owner=user) | Q(shares__shared_with=user)
        ).distinct(),
        pk=doc_id,
    )

    is_owner = doc.owner == user
    if not is_owner:
        share = doc.shares.filter(shared_with=user).first()
        if not share or share.permission != 'edit':
            ctx = _build_context(request, active_doc=doc, save_status='error')
            return render(request, 'editor/editor.html', ctx, status=403)

    doc.title   = request.POST.get('title', doc.title).strip() or 'Untitled Document'
    doc.content = request.POST.get('content', doc.content)
    doc.save()

    ctx = _build_context(request, active_doc=doc, save_status='saved')
    return render(request, 'editor/editor.html', ctx)


@require_http_methods(['POST'])
def doc_import(request):
    user    = _get_active_user(request)
    title   = request.POST.get('title', 'Imported Document').strip() or 'Imported Document'
    content = request.POST.get('content', '')
    doc = Document.objects.create(title=title, content=content, owner=user)
    return redirect('doc-edit', doc_id=doc.id)


@require_http_methods(['POST'])
def doc_share(request, doc_id):
    user = _get_active_user(request)
    doc  = get_object_or_404(Document, pk=doc_id, owner=user)

    username   = request.POST.get('username', '').strip()
    permission = request.POST.get('permission', 'view')

    if username and permission in ('view', 'edit'):
        try:
            target = User.objects.get(username=username)
            if target != user:
                DocumentShare.objects.update_or_create(
                    document=doc,
                    shared_with=target,
                    defaults={'permission': permission},
                )
        except User.DoesNotExist:
            pass

    ctx = _build_context(request, active_doc=doc, open_share_modal=True)
    return render(request, 'editor/editor.html', ctx)


@require_http_methods(['POST'])
def doc_revoke(request, doc_id, username):
    user = _get_active_user(request)
    doc  = get_object_or_404(Document, pk=doc_id, owner=user)
    DocumentShare.objects.filter(document=doc, shared_with__username=username).delete()

    ctx = _build_context(request, active_doc=doc, open_share_modal=True)
    return render(request, 'editor/editor.html', ctx)
