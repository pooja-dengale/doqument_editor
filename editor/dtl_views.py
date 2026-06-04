"""
DTL (Django Template Language) views.
Replaces the React frontend with server-rendered pages.
Session-based authentication — no tokens needed.
"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Document, DocumentShare


# ── Auth ─────────────────────────────────────────────────────────────────────

def login_view(request):
    from django.contrib.auth.forms import AuthenticationForm
    if request.user.is_authenticated:
        return redirect('editor-home')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect(request.GET.get('next', 'editor-home'))

    return render(request, 'editor/login.html', {'form': form})


@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    return redirect('login')


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_sidebar_docs(user):
    """Return (my_docs, shared_docs) for the sidebar."""
    my_docs = Document.objects.filter(owner=user).order_by('-updated_at')

    shared_qs = Document.objects.filter(
        shares__shared_with=user
    ).exclude(owner=user).distinct().order_by('-updated_at')

    # Annotate each shared doc with the user's permission level
    shared_docs = []
    for doc in shared_qs:
        share = doc.shares.filter(shared_with=user).first()
        doc.my_permission = share.permission if share else 'view'
        shared_docs.append(doc)

    return my_docs, shared_docs


def _build_context(request, active_doc=None, save_status=None, open_share_modal=False):
    """Build the full template context."""
    my_docs, shared_docs = _get_sidebar_docs(request.user)

    can_edit = False
    is_owner = False

    if active_doc:
        is_owner = active_doc.owner == request.user
        if is_owner:
            can_edit = True
        else:
            share = active_doc.shares.filter(shared_with=request.user).first()
            can_edit = share and share.permission == 'edit'

        # Users that can still be shared with (exclude owner + already shared)
        shared_usernames = list(active_doc.shares.values_list('shared_with__username', flat=True))
        shared_usernames.append(active_doc.owner.username)
        shareable_users = User.objects.exclude(username__in=shared_usernames)
    else:
        shareable_users = User.objects.none()

    return {
        'my_docs':           my_docs,
        'shared_docs':       shared_docs,
        'active_doc':        active_doc,
        'can_edit':          can_edit,
        'is_owner':          is_owner,
        'shareable_users':   shareable_users,
        'save_status':       save_status,
        'open_share_modal':  open_share_modal,
    }


# ── Views ─────────────────────────────────────────────────────────────────────

@login_required
def editor_home(request):
    """Landing page — shows sidebar, no active document."""
    ctx = _build_context(request)
    return render(request, 'editor/editor.html', ctx)


@login_required
def doc_new(request):
    """Create a new blank document and open it."""
    doc = Document.objects.create(
        title='Untitled Document',
        content='',
        owner=request.user,
    )
    return redirect('doc-edit', doc_id=doc.id)


@login_required
def doc_edit(request, doc_id):
    """Open an existing document in the editor."""
    # Users can only access docs they own or are shared with
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
    """Save title + content for a document."""
    doc = get_object_or_404(
        Document.objects.filter(
            Q(owner=request.user) | Q(shares__shared_with=request.user)
        ).distinct(),
        pk=doc_id,
    )

    # Permission check
    is_owner = doc.owner == request.user
    if not is_owner:
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
    """Create a document from imported .txt / .md file content."""
    title   = request.POST.get('title', 'Imported Document').strip() or 'Imported Document'
    content = request.POST.get('content', '')
    doc = Document.objects.create(title=title, content=content, owner=request.user)
    return redirect('doc-edit', doc_id=doc.id)


@login_required
@require_http_methods(['POST'])
def doc_share(request, doc_id):
    """Grant a user access to a document (owner only)."""
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

    # Reopen editor with share modal still open
    ctx = _build_context(request, active_doc=doc, open_share_modal=True)
    return render(request, 'editor/editor.html', ctx)


@login_required
@require_http_methods(['POST'])
def doc_revoke(request, doc_id, username):
    """Revoke a user's access to a document (owner only)."""
    doc = get_object_or_404(Document, pk=doc_id, owner=request.user)
    DocumentShare.objects.filter(
        document=doc,
        shared_with__username=username,
    ).delete()

    ctx = _build_context(request, active_doc=doc, open_share_modal=True)
    return render(request, 'editor/editor.html', ctx)
