from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Subscription
from .forms import SubscriptionForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import Subscription, UserProfile


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'subscriptions/landing.html')


@login_required(login_url='login')
def dashboard(request):
    subscriptions = Subscription.objects.filter(user=request.user, is_active=True)

    total_monthly = 0
    for sub in subscriptions:
        if sub.billing_cycle == 'monthly':
            total_monthly += sub.price
        else:
            total_monthly += sub.price / 12

    profile, created = UserProfile.objects.get_or_create(user=request.user)
    budget = profile.monthly_budget

    if budget > 0:
        percent = (total_monthly / budget) * 100
    else:
        percent = 0

    context = {
        'subscriptions': subscriptions,
        'total_monthly': round(total_monthly, 2),
        'budget': budget,
        'percent': min(round(percent, 1), 100),
        'is_over_budget': total_monthly > budget,
        'chart_labels': [sub.name for sub in subscriptions],
        'chart_data': [float(sub.price) if sub.billing_cycle == 'monthly' else float(sub.price / 12) for sub in
                       subscriptions],
    }

    return render(request, 'subscriptions/dashboard.html', context)


@login_required(login_url='/admin/login/')
def add_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            new_sub = form.save(commit=False)
            new_sub.user = request.user
            new_sub.save()
            messages.success(request, f"Успешно добави абонамент за {new_sub.name}!")
            return redirect('dashboard')
    else:
        form = SubscriptionForm()

    return render(request, 'subscriptions/add_subscription.html', {'form': form})

@login_required(login_url='/admin/login/')
def edit_subscription(request, pk):
    sub = get_object_or_404(Subscription, pk=pk, user=request.user)

    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=sub)
        if form.is_valid():
            form.save()
            messages.info(request, "Абонаментът беше обновен успешно.")
            return redirect('dashboard')
    else:
        form = SubscriptionForm(instance=sub)

    return render(request, 'subscriptions/edit_subscription.html', {'form': form, 'sub': sub})


@login_required(login_url='/admin/login/')
def cancel_subscription(request, pk):
    sub = get_object_or_404(Subscription, pk=pk, user=request.user)
    sub.is_active = False
    sub.save()
    messages.warning(request, f"Абонаментът за {sub.name} е прекратен.")
    return redirect('dashboard')


def logout_view(request):
    logout(request)
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Добре дошъл, {user.username}! Профилът ти е създаден.")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'subscriptions/signup.html', {'form': form})

@login_required(login_url='login')
def archived_subscriptions(request):
    archived_subs = Subscription.objects.filter(user=request.user, is_active=False).order_by('-id')
    return render(request, 'subscriptions/archive.html', {'archived_subs': archived_subs})

@login_required(login_url='login')
def reactivate_subscription(request, pk):
    sub = get_object_or_404(Subscription, pk=pk, user=request.user)
    sub.is_active = True
    sub.save()
    messages.success(request, f"Абонаментът за {sub.name} е възстановен!")
    return redirect('dashboard')