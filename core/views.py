from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import FileResponse, HttpResponseForbidden
from core.forms import AgentForm, StoreForm, BillDateForm, BillForm
from core.models import Agent, Manager, Store, Transaction, BillDate, Bill, Product
from .utils import generate_bill_pdf
from django.contrib.auth import login as auth_login
from django import forms
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.forms import AgentForm
from .models import Agent, Manager
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Agent, Manager

# Home page with Signup/Login links
def home(request):
    return render(request, 'home.html')

# === AUTH SYSTEM ===


from django.shortcuts import render
from core.forms import AgentForm

def test_agent_form(request):
    form = AgentForm()
    return render(request, 'test_form.html', {'form': form})


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




from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib import messages
from core.forms import AgentForm
from .models import Manager

@login_required
def agent_create(request):

    print(f"Request User: {request.user} (ID: {request.user.id})")
    
    # Ensure only Managers can access
    if not request.user.groups.filter(name='Manager').exists():
        return HttpResponseForbidden("Unauthorized access. You must be a Manager.")

    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            try:
                # Get manager instance
                manager = Manager.objects.get(user=request.user)

                # Save agent without committing to DB yet
                agent = form.save(commit=False)
                agent.manager = manager
                agent.save()  # Save agent to DB

                # Add the new user to the Agent group
                agent_group, _ = Group.objects.get_or_create(name='Agent')
                agent.user.groups.add(agent_group)

                messages.success(request, "Agent created successfully.")
                return redirect('manager_dashboard')

            except Manager.DoesNotExist:
                return HttpResponseForbidden("Manager record not found.")
            except Exception as e:
                form.add_error(None, f"An error occurred while saving: {str(e)}")
    else:
        form = AgentForm()
    
    return render(request, 'manager/agent_form.html', {
        'form': form,
        'form_title': 'Create Agent'
    })



 
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
        print("\n\n\n\n\n",request.POST['agent_id'],"\n\n\n\n\n")
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


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .models import Agent, Transaction, AgentBalance
from django.utils import timezone
from datetime import datetime
from django.db.models import Sum, Case, When, Value, DecimalField, F
import logging

# Set up logging to debug the balance calculation
logger = logging.getLogger(__name__)

def manager_dashboard(request):
    # Annotate agents with their balance using the related name 'transaction'
    agents = Agent.objects.annotate(
        balance=Sum(
            Case(
                When(transaction__transaction_type='credit', then=-F('transaction__amount')),
                When(transaction__transaction_type='return', then=F('transaction__amount')),
                default=Value(0, output_field=DecimalField()),
                output_field=DecimalField()
            ),
            output_field=DecimalField()
        )
    )


    # Update AgentBalance for each agent
    for agent in agents:
        agent_balance_obj, created = AgentBalance.objects.get_or_create(
            agent=agent,
            defaults={'amount': agent.balance if agent.balance is not None else 0}
        )
        if agent_balance_obj.amount != (agent.balance if agent.balance is not None else 0):
            agent_balance_obj.amount = agent.balance if agent.balance is not None else 0
            agent_balance_obj.save()
            logger.debug(f"Updated AgentBalance for {agent.name}: {agent_balance_obj.amount}")

    transactions = Transaction.objects.all()

    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Filter transactions
        filtered_transactions = transactions
        if agent_id:
            filtered_transactions = filtered_transactions.filter(agent__agent_id=agent_id)
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            filtered_transactions = filtered_transactions.filter(transaction_date__gte=start_date)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            filtered_transactions = filtered_transactions.filter(transaction_date__lte=end_date)

        return render(request, 'manager/dashboard.html', {
            'agents': agents,
            'transactions': filtered_transactions,
            'selected_agent': agent_id,
            'start_date': start_date,
            'end_date': end_date
        })

    # GET request: show all transactions
    return render(request, 'manager/dashboard.html', {
        'agents': agents,
        'transactions': transactions
    })



# Update login_view to redirect to manager_dashboard
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.groups.filter(name='Manager').exists():
                return redirect('manager_dashboard')
            elif user.groups.filter(name='Agent').exists():
                return redirect('agent_dashboard')
            else:
                messages.error(request, 'User does not belong Gluonsto any authorized group.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')