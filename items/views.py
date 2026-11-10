from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Item, ClaimRequest, Notification
from .forms import ItemForm, ClaimRequestForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = UserCreationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Your CampusFind account was created!')
        return redirect('dashboard')

    return render(request, 'items/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password

        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'items/login.html')



@login_required
def dashboard_view(request):
    # Admins can see ALL reports.
    # Students can see only approved reports.
    if request.user.is_staff:
        visible_items = Item.objects.all().order_by('-created_at')
    else:
        visible_items = Item.objects.filter(
            status='Approved'
        ).order_by('-created_at')

    # Search by title or description
    search_query = request.GET.get('q', '').strip()

    if search_query:
        from django.db.models import Q
        visible_items = visible_items.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filter by category
    category = request.GET.get('category', '')

    if category:
        visible_items = visible_items.filter(category=category)

    # Filter by Lost or Found
    report_type = request.GET.get('report_type', '')

    if report_type:
        visible_items = visible_items.filter(report_type=report_type)

    missing_items = Item.objects.filter(report_type='Lost').order_by('-created_at')

    if not request.user.is_staff:
        missing_items = missing_items.filter(status='Approved')

    my_reports = Item.objects.filter(
        reported_by=request.user
    ).order_by('-created_at')

    my_claims = ClaimRequest.objects.filter(
        claimant=request.user
    ).select_related('item').order_by('-created_at')

    my_notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    unread_count = my_notifications.filter(is_read=False).count()

    return render(request, 'items/dashboard.html', {
        'items': visible_items,
        'missing_items': missing_items,
        'my_reports': my_reports,
        'my_claims': my_claims,
        'search_query': search_query,
        'selected_category': category,
        'selected_report_type': report_type,
        'categories': Item.CATEGORY_CHOICES,
        'my_notifications': my_notifications,
        'unread_count': unread_count,

        # Admin dashboard statistics
        'total_items': Item.objects.count(),
        'lost_items': Item.objects.filter(report_type='Lost').count(),
        'found_items': Item.objects.filter(report_type='Found').count(),
        'pending_reports': Item.objects.filter(status='Pending').count(),
        'pending_claims': ClaimRequest.objects.filter(status='Pending').count(),
        'returned_items': Item.objects.filter(status='Returned').count(),
    })


@login_required
def report_item_view(request):
    form = ItemForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.reported_by = request.user
        item.status = 'Pending'
        item.save()

        messages.success(
            request,
            'Your report was submitted and is waiting for admin approval.'
        )
        return redirect('dashboard')

    return render(request, 'items/report_item.html', {'form': form})


@login_required
def claim_item_view(request, item_id):
    item = get_object_or_404(
        Item,
        id=item_id,
        status='Approved',
        report_type='Found'
    )

    if item.reported_by == request.user:
        messages.error(request, "You cannot claim your own reported item.")
        return redirect('dashboard')

    existing_claim = ClaimRequest.objects.filter(
        item=item,
        claimant=request.user
    ).exists()

    if existing_claim:
        messages.warning(request, "You have already submitted a claim for this item.")
        return redirect('dashboard')

    form = ClaimRequestForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        ClaimRequest.objects.create(
            item=item,
            claimant=request.user,
            message=form.cleaned_data['message']
        )

        messages.success(request, "Your claim request was submitted.")
        return redirect('dashboard')

    return render(request, 'items/claim_item.html', {
        'form': form,
        'item': item
    })


@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')


@login_required
@require_POST
def mark_notification_read_view(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    messages.success(request, "Notification marked as read.")
    return redirect('dashboard')
