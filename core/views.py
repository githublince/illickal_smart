import logging
from datetime import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Sum, Case, When, Value, DecimalField, F
from django.forms import modelformset_factory
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from core.forms import AgentForm, StoreForm, BillDateForm, BillForm
from core.models import Agent, Manager, Store, Transaction, BillDate, Bill, Product

from .models import Agent, Manager, Transaction, AgentBalance
from .utils import generate_bill_pdf

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



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db import transaction as db_transaction
from .forms import TransactionForm, ProductFormSet
from .models import Manager, Transaction, ManagerAgentTransaction
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db import transaction as db_transaction
from .forms import TransactionForm, ProductFormSet
from .models import Manager, Transaction, ManagerAgentTransaction
import logging

logger = logging.getLogger(__name__)

@login_required
def manager_agent_transaction_create(request):
    if not request.user.groups.filter(name='Manager').exists():
        return HttpResponseForbidden("Unauthorized")
    
    if request.method == 'POST':
        transaction_form = TransactionForm(request.POST)
        product_formset = ProductFormSet(request.POST, prefix='products')
        
        if transaction_form.is_valid() and product_formset.is_valid():
            valid_forms = [
                form for form in product_formset
                if form.cleaned_data and form.cleaned_data.get('product')
            ]
            if not valid_forms:
                messages.error(request, "Please add at least one product to the transaction.")
            else:
                try:
                    with db_transaction.atomic():
                        manager = Manager.objects.get(user=request.user)
                        transaction = transaction_form.save(commit=False)
                        total_amount = sum(
                            form.cleaned_data['quantity'] * form.cleaned_data['product'].rr_price
                            for form in valid_forms
                        )
                        if total_amount <= 0:
                            raise ValueError("Total amount must be positive.")
                        transaction.amount = total_amount
                        transaction.transaction_type = 'credit'
                        transaction.save()
                        
                        for form in valid_forms:
                            mat = form.save(commit=False)
                            mat.transaction = transaction
                            mat.manager = manager
                            mat.agent = transaction.agent
                            mat.transaction_date = transaction.transaction_date
                            mat.save()
                        
                        messages.success(request, "Manager-Agent Transaction created successfully.")
                        return redirect('manager_agent_transaction_list')
                except Exception as e:
                    logger.error(f"Transaction creation failed: {str(e)}")
                    messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        transaction_form = TransactionForm()
        product_formset = ProductFormSet(prefix='products', initial=[{'quantity': 1}])  # Exactly one empty form
    
    return render(request, 'manager/manager_agent_transaction_form.html', {
        'transaction_form': transaction_form,
        'product_formset': product_formset,
        'form_title': 'Create Manager-Agent Transaction'
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseForbidden
from .models import ManagerAgentTransaction
from datetime import datetime, date
from calendar import monthrange, month_name
from django.utils.timezone import now

@login_required
def manager_agent_transaction_list(request):
    if not request.user.groups.filter(name='Manager').exists():
        return HttpResponseForbidden("Unauthorized")
    
    # Get current date and query parameters
    today = now().date()
    selected_date = request.GET.get('date', today.strftime('%Y-%m-%d'))
    show_all = request.GET.get('show_all', 'false').lower() == 'true'
    
    try:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today
    
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Validate year and month
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Calculate previous and next month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    # Generate calendar data
    _, num_days = monthrange(year, month)
    first_day = date(year, month, 1).weekday()  # 0=Mon, 6=Sun
    calendar_days = []
    week = [None] * first_day + [date(year, month, d) for d in range(1, num_days + 1)]
    while week:
        calendar_days.append(week[:7])
        week = week[7:] if len(week) > 7 else []
    if len(week) > 0:
        calendar_days.append(week + [None] * (7 - len(week)))

    # Fetch distinct transaction dates for the current month
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)
    transaction_dates = set(
        ManagerAgentTransaction.objects.filter(
            transaction_date__range=[start_date, end_date]
        ).values_list('transaction_date', flat=True).distinct()
    )

    # Fetch transactions
    if show_all:
        transactions = ManagerAgentTransaction.objects.select_related(
            'transaction', 'product', 'manager', 'agent'
        ).order_by('transaction__transaction_date', 'transaction__transaction_id', 'product__name')
    else:
        transactions = ManagerAgentTransaction.objects.select_related(
            'transaction', 'product', 'manager', 'agent'
        ).filter(transaction_date=selected_date).order_by('transaction__transaction_id', 'product__name')

    # Group transactions by transaction_id and calculate grand total
    grouped_transactions = {}
    grand_total = 0
    for txn in transactions:
        txn_id = txn.transaction.transaction_id
        if txn_id not in grouped_transactions:
            grouped_transactions[txn_id] = {
                'transaction': txn.transaction,
                'items': [],
                'total': 0
            }
        grouped_transactions[txn_id]['items'].append(txn)
        grouped_transactions[txn_id]['total'] += txn.total_price
        grand_total += txn.total_price

    return render(request, 'manager/manager_agent_transaction_list.html', {
        'grouped_transactions': grouped_transactions,
        'calendar_days': calendar_days,
        'selected_date': selected_date,
        'today': today,
        'year': year,
        'month': month,
        'month_name': month_name[month],
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'show_all': show_all,
        'grand_total': grand_total,
        'transaction_dates': transaction_dates,
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from .forms import ProductCreateForm

@login_required
def product_create(request):
    if not request.user.groups.filter(name='Manager').exists():
        return HttpResponseForbidden("Unauthorized")
    
    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Product created successfully.")
                return redirect('manager_dashboard')  # Or a product list view
            except Exception as e:
                messages.error(request, f"Error creating product: {str(e)}")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ProductCreateForm()
    
    return render(request, 'manager/product_create.html', {
        'form': form,
        'form_title': 'Create Product'
    })



import logging
from django.http import JsonResponse
from .models import Product

logger = logging.getLogger(__name__)

def product_search(request):
    try:
        query = request.GET.get('q', '')
        products = Product.objects.filter(name__icontains=query)[:10]
        results = [
            {
                'id': product.product_id,
                'text': product.name,  # Select2 expects 'text' for display
                'image': product.get_image_data(),
                'rr_price': float(product.rr_price)  # Convert Decimal to float for JSON
            }
            for product in products
        ]
        return JsonResponse({'results': results})
    except Exception as e:
        logger.error(f"Error in product_search: {str(e)}")
        return JsonResponse({'results': []}, status=500)
    