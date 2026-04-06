from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Subscription
from .forms import SubscriptionForm
from django.shortcuts import render, redirect, get_object_or_404


@login_required(login_url='/admin/login/')
def dashboard(request):
    user_subs = Subscription.objects.filter(user=request.user, is_active=True)

    total_monthly = 0
    chart_labels = []
    chart_data = []

    for sub in user_subs:
        monthly_cost = float(sub.price) if sub.billing_cycle == 'monthly' else float(sub.price) / 12
        total_monthly += monthly_cost

        chart_labels.append(sub.name)
        chart_data.append(round(monthly_cost, 2))

    context = {
        'subscriptions': user_subs,
        'total_monthly': round(total_monthly, 2),
        'chart_labels': chart_labels,
        'chart_data': chart_data,
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
            return redirect('dashboard')
    else:
        form = SubscriptionForm(instance=sub)

    return render(request, 'subscriptions/edit_subscription.html', {'form': form, 'sub': sub})


@login_required(login_url='/admin/login/')
def cancel_subscription(request, pk):
    sub = get_object_or_404(Subscription, pk=pk, user=request.user)
    sub.is_active = False
    sub.save()
    return redirect('dashboard')