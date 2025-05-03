from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import FileResponse, HttpResponseForbidden
from .forms import AgentForm, StoreForm, BillDateForm, BillForm
from .models import Agent, Manager, Store, Transaction, BillDate, Bill, Product
from .utils import generate_bill_pdf
from django.contrib.auth import login as auth_login


# Home page with Signup/Login links
def home(request):
    return render(request, 'home.html')

# === AUTH SYSTEM ===

# core/views.py

from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Agent, Manager


def signup_manager(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        user.save()
        manager_group, created = Group.objects.get_or_create(name='Manager')
        user.groups.add(manager_group)

        Manager.objects.create(user=user, username=username, password=password)

        messages.success(request, 'Manager account created. Please login.')
        return redirect('login')
    return render(request, 'registration/signup.html')

@login_required
def agent_dashboard(request):
    if not request.user.groups.filter(name='Agent').exists():
        return HttpResponseForbidden("Unauthorized")
    return render(request, 'agent/dashboard.html')


@login_required
def manager_dashboard(request):
    if not request.user.groups.filter(name='Manager').exists():
        return HttpResponseForbidden("Unauthorized")
    agents = Agent.objects.all()
    transactions = Transaction.objects.all()
    return render(request, 'manager/dashboard.html', {
        'agents': agents,
        'transactions': transactions
    })

# === AGENT FEATURES ===

@login_required
def store_create(request):
    if not request.user.groups.filter(name='Agent').exists():
        return HttpResponseForbidden("Unauthorized")
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Store saved successfully.")
            return redirect('agent_dashboard')
    else:
        form = StoreForm()
    return render(request, 'agent/store_form.html', {'form': form})


@login_required
def create_bill(request):
    if not request.user.groups.filter(name='Agent').exists():
        return HttpResponseForbidden("Unauthorized")
    BillFormSet = modelformset_factory(Bill, form=BillForm, extra=3)
    if request.method == 'POST':
        bill_date_form = BillDateForm(request.POST)
        formset = BillFormSet(request.POST)
        if bill_date_form.is_valid() and formset.is_valid():
            bill_date = bill_date_form.save()
            for form in formset:
                bill = form.save(commit=False)
                bill.billno = bill_date
                bill.save()
            messages.success(request, "Bill created successfully.")
            return redirect('download_bill', billno=bill_date.billno)
    else:
        bill_date_form = BillDateForm()
        formset = BillFormSet(queryset=Bill.objects.none())
    return render(request, 'agent/create_bill.html', {
        'bill_date_form': bill_date_form,
        'formset': formset
    })


@login_required
def download_bill(request, billno):
    if not request.user.groups.filter(name='Agent').exists():
        return HttpResponseForbidden("Unauthorized")
    pdf = generate_bill_pdf(billno)
    return FileResponse(pdf, as_attachment=True, filename=f'{billno}.pdf')

# === MANAGER FEATURES ===

@login_required
def agent_create(request):
    if not request.user.groups.filter(name='Manager').exists():
        return HttpResponseForbidden("Unauthorized")
    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Agent created.")
            return redirect('manager_dashboard')
    else:
        form = AgentForm()
    return render(request, 'manager/agent_form.html', {'form': form})


@login_required
def agent_update(request, pk):
    if not request.user.groups.filter(name='Manager').exists():
        return HttpResponseForbidden("Unauthorized")
    agent = get_object_or_404(Agent, pk=pk)
    if request.method == 'POST':
        form = AgentForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, "Agent updated.")
            return redirect('manager_dashboard')
    else:
        form = AgentForm(instance=agent)
    return render(request, 'manager/agent_form.html', {'form': form})


@login_required
def agent_delete(request, pk):
    if not request.user.groups.filter(name='Manager').exists():
        return HttpResponseForbidden("Unauthorized")
    agent = get_object_or_404(Agent, pk=pk)
    agent.delete()
    messages.success(request, "Agent deleted.")
    return redirect('manager_dashboard')


@login_required
def agent_block_toggle(request, pk):
    if not request.user.groups.filter(name='Manager').exists():
        return HttpResponseForbidden("Unauthorized")
    agent = get_object_or_404(Agent, pk=pk)
    agent.is_active = not agent.is_active
    agent.save()
    msg = "blocked" if not agent.is_active else "unblocked"
    messages.info(request, f"Agent {msg}.")
    return redirect('manager_dashboard')


@login_required
def transaction_create(request):
    if not request.user.groups.filter(name='Manager').exists():
        return HttpResponseForbidden("Unauthorized")
    if request.method == 'POST':
        agent_id = request.POST['agent_id']
        amount = request.POST['amount']
        type_ = request.POST['transaction_type']
        agent = Agent.objects.get(pk=agent_id)
        Transaction.objects.create(
            agent=agent,
            amount=amount,
            transaction_type=type_
        )
        messages.success(request, "Transaction added.")
        return redirect('manager_dashboard')
    agents = Agent.objects.all()
    return render(request, 'manager/transaction_form.html', {'agents': agents})


@login_required
def agent_create(request):
    if not request.user.groups.filter(name='Manager').exists():
        return HttpResponseForbidden("Unauthorized")

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        name = request.POST['name']
        phone_number = request.POST['phone_number']
        whatsapp_number = request.POST['whatsapp_number']
        address = request.POST['address']
        pincode = request.POST['pincode']

        user = User.objects.create_user(username=username, password=password)
        agent_group, _ = Group.objects.get_or_create(name='Agent')
        user.groups.add(agent_group)

        manager = Manager.objects.get(user=request.user)
        Agent.objects.create(
            user=user,
            name=name,
            phone_number=phone_number,
            whatsapp_number=whatsapp_number,
            address=address,
            pincode=pincode,
            manager=manager
        )
        messages.success(request, "Agent created successfully.")
        return redirect('manager_dashboard')

    return render(request, 'manager/agent_form.html')



        
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Log the user in to establish a session
            if user.groups.filter(name='Manager').exists():
                return redirect('manager_dashboard')
            elif user.groups.filter(name='Agent').exists():
                return redirect('agent_dashboard')
            else:
                messages.error(request, 'User does not belong to any authorized group.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')