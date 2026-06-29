from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .models import Subscription, UserProfile, Company
from .forms import SubscriptionForm, CompanySettingsForm
from .ai_script import extract_invoice_data
import csv
from django.http import HttpResponse

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'subscriptions/landing.html')

def get_user_company(user):
    profile, created = UserProfile.objects.get_or_create(user=user)
    if not profile.company:
        default_company = Company.objects.create(name=f"Компания на {user.username}")
        profile.company = default_company
        profile.save()
    return profile.company

@login_required(login_url='login')
def dashboard(request):
    company = get_user_company(request.user)

    subscriptions = Subscription.objects.filter(company=company, is_active=True)
    canceled_subs = Subscription.objects.filter(company=company, is_active=False)

    EXCHANGE_RATES = {
        'лв.': 1.0, 'BGN': 1.0,
        'EUR': 1.95, '€': 1.95,
        'USD': 1.80, '$': 1.80
    }

    total_monthly = 0
    potential_savings = 0
    monthly_subs_count = 0
    upcoming_payments = []
    today = date.today()

    for sub in subscriptions:
        rate = EXCHANGE_RATES.get(sub.currency, 1.0)
        price_in_bgn = float(sub.price) * rate

        if sub.billing_cycle == 'monthly':
            total_monthly += price_in_bgn
            yearly_cost = price_in_bgn * 12
            potential_savings += yearly_cost * 0.20
            monthly_subs_count += 1
        else:
            total_monthly += price_in_bgn / 12

        if sub.start_date:
            next_date = sub.start_date
            while next_date < today:
                if sub.billing_cycle == 'monthly':
                    next_date += timedelta(days=30)
                else:
                    next_date += timedelta(days=365)

            days_until = (next_date - today).days

            if 0 <= days_until <= 14:
                upcoming_payments.append({
                    'name': sub.name,
                    'days_until': days_until,
                    'amount': sub.price,
                    'currency': sub.currency,
                    'department': sub.department.name if sub.department else 'Общ разход'
                })

    upcoming_payments.sort(key=lambda x: x['days_until'])

    saved_monthly = 0
    for sub in canceled_subs:
        rate = EXCHANGE_RATES.get(sub.currency, 1.0)
        price_in_bgn = float(sub.price) * rate
        if sub.billing_cycle == 'monthly':
            saved_monthly += price_in_bgn
        else:
            saved_monthly += price_in_bgn / 12

    budget = float(company.monthly_budget)
    percent = (total_monthly / budget) * 100 if budget > 0 else 0
    
    context = {
        'company_name': company.name, 
        'subscriptions': subscriptions,
        'total_monthly': round(total_monthly, 2),
        'budget': budget,
        'percent': min(round(percent, 1), 100),
        'is_over_budget': total_monthly > budget,
        'chart_labels': [sub.name for sub in subscriptions],
        'chart_data': [float(sub.price) * EXCHANGE_RATES.get(sub.currency, 1.0) if sub.billing_cycle == 'monthly' else (float(sub.price) * EXCHANGE_RATES.get(sub.currency,1.0)) / 12 for sub in subscriptions],
        'saved_monthly': round(saved_monthly, 2),
        'canceled_count': canceled_subs.count(),
        'potential_savings': round(potential_savings, 2),
        'monthly_subs_count': monthly_subs_count,
        'upcoming_payments': upcoming_payments,
    }

    return render(request, 'subscriptions/dashboard.html', context)

@login_required(login_url='login')
def settings(request):
    company = get_user_company(request.user)
    
    if request.method == 'POST':
        form = CompanySettingsForm(request.POST)
        if form.is_valid():
            company.name = form.cleaned_data['name']
            company.monthly_budget = form.cleaned_data['monthly_budget']
            company.save()
            
            messages.success(request, 'Настройките на профила са обновени успешно!')
            return redirect('dashboard')
    else:
        form = CompanySettingsForm(initial={
            'name': company.name, 
            'monthly_budget': company.monthly_budget
        })
        
    return render(request, 'subscriptions/settings.html', {'form': form})


@login_required(login_url='/admin/login/')
def add_subscription(request):
    company = get_user_company(request.user)
    
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, request.FILES) 
        if form.is_valid():
            new_sub = form.save(commit=False)
            new_sub.company = company 
            new_sub.owner = request.user 

            new_sub.save()

            if new_sub.invoice_file:
                extracted_data = extract_invoice_data(new_sub.invoice_file.path)
                
                if extracted_data:
                    new_sub.name = extracted_data.get('name', new_sub.name)
                    new_sub.price = extracted_data.get('price', new_sub.price)
                    new_sub.currency = extracted_data.get('currency', new_sub.currency)

                    if hasattr(new_sub, 'is_ai_extracted'):
                        new_sub.is_ai_extracted = True
                        
                    new_sub.save() 
                    messages.success(request, f"🤖 AI успешно разчете документа: {new_sub.name} ({new_sub.price} {new_sub.currency})!")
                else:
                    messages.warning(request, "Фактурата е качена, но AI не успя да я разчете ясно.")
            else:
                messages.success(request, f"Успешно добавен софтуер {new_sub.name}!")
                
            return redirect('dashboard')
    else:
        form = SubscriptionForm()
        form.fields['department'].queryset = company.departments.all()

    return render(request, 'subscriptions/add_subscription.html', {'form': form})


@login_required(login_url='/admin/login/')
def edit_subscription(request, pk):
    company = get_user_company(request.user)
    sub = get_object_or_404(Subscription, pk=pk, company=company) 

    if request.method == 'POST':
        form = SubscriptionForm(request.POST, request.FILES, instance=sub)
        if form.is_valid():
            form.save()
            messages.info(request, "Абонаментът беше обновен успешно.")
            return redirect('dashboard')
    else:
        form = SubscriptionForm(instance=sub)
        form.fields['department'].queryset = company.departments.all()

    return render(request, 'subscriptions/edit_subscription.html', {'form': form, 'sub': sub})


@login_required(login_url='/admin/login/')
def cancel_subscription(request, pk):
    company = get_user_company(request.user)
    sub = get_object_or_404(Subscription, pk=pk, company=company)
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
            get_user_company(user)
            login(request, user)
            messages.success(request, f"Добре дошъл, {user.username}! Фирменият ти профил е създаден.")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'subscriptions/signup.html', {'form': form})


@login_required(login_url='login')
def archived_subscriptions(request):
    company = get_user_company(request.user)
    archived_subs = Subscription.objects.filter(company=company, is_active=False).order_by('-id')
    return render(request, 'subscriptions/archive.html', {'archived_subs': archived_subs})

@login_required(login_url='login')
def reactivate_subscription(request, pk):
    company = get_user_company(request.user)
    sub = get_object_or_404(Subscription, pk=pk, company=company)
    sub.is_active = True
    sub.save()
    messages.success(request, f"Абонаментът за {sub.name} е възстановен!")
    return redirect('dashboard')

@login_required(login_url='login')
def export_subscriptions_csv(request):
    company = get_user_company(request.user)
    subscriptions = Subscription.objects.filter(company=company)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="subscriptions_export.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Софтуер / Услуга', 'Отдел', 'Цена', 'Валута', 'Цикъл', 'Статус'])

    for sub in subscriptions:
        status = 'Активен' if sub.is_active else 'Прекратен'
        department = sub.department.name if sub.department else 'Общ разход'
        
        writer.writerow([
            sub.name, 
            department, 
            sub.price, 
            sub.currency, 
            sub.billing_cycle, 
            status
        ])

    return response

import json
from django.shortcuts import render

def analytics_view(request):
    oracle_labels = ['Яну', 'Фев', 'Мар', 'Апр', 'Май', 'Юни', 'Юли (Сега)', 'Авг (AI)', 'Сеп (AI)', 'Окт (AI)']
    oracle_past_data = [3200, 3400, 3100, 4500, 4200, 4100, 4300, None, None, None]
    oracle_future_data = [None, None, None, None, None, None, 4300, 4600, 4100, 3800]

    sky_labels = ['AWS', 'Salesforce', 'Google W.S.', 'Slack', 'Figma']
    sky_data = [2500, 1800, 950, 600, 450]

    heatmap_data = [
        {'month': 'Януари', 'amount': '1,200', 'intensity': 1},
        {'month': 'Февруари', 'amount': '2,500', 'intensity': 2},
        {'month': 'Март', 'amount': '1,400', 'intensity': 1},
        {'month': 'Април', 'amount': '8,900', 'intensity': 4},
        {'month': 'Май', 'amount': '4,500', 'intensity': 3},
        {'month': 'Юни', 'amount': '2,100', 'intensity': 2},
        {'month': 'Юли', 'amount': '1,100', 'intensity': 1},
        {'month': 'Август', 'amount': '900', 'intensity': 1},
        {'month': 'Септември', 'amount': '5,600', 'intensity': 3},
        {'month': 'Октомври', 'amount': '7,800', 'intensity': 4},
        {'month': 'Ноември', 'amount': '3,200', 'intensity': 2},
        {'month': 'Декември', 'amount': '6,100', 'intensity': 3},
    ]

    context = {
        'total_spent_year': '45,230',
        'predicted_savings': '3,400',
        'oracle_labels': json.dumps(oracle_labels),
        'oracle_past_data': json.dumps(oracle_past_data),
        'oracle_future_data': json.dumps(oracle_future_data),
        'sky_labels': json.dumps(sky_labels),
        'sky_data': json.dumps(sky_data),
        'heatmap_data': heatmap_data,
    }
    
    return render(request, 'subscriptions/analytics.html', context)