from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Profile, TicketStatus

def Index_function(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        mobile_number = request.POST['mobile_number']
        password = request.POST['password']
        role = request.POST['role']

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('Index_function')

        user = CustomUser.objects.create_user(email=email, password=password, first_name=name)
        user.save()

        profile = Profile(user=user, mobile_number=mobile_number, role=role)
        profile.save()

        messages.success(request, 'Account created successfully')
        return redirect('login')

    return render(request, 'index.html')

def login_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            profile = Profile.objects.get(user=user)
            if profile.role == '1':
                return redirect('staff_home')
            elif profile.role == '2':
                return redirect('customer_home')
            else:
                return redirect('admin_home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'index.html')




#Admin_panel 
#-----------------------------------------------------------------------------------------------------------------------------

@login_required
def admin_home(request):
    tickets_count = Ticket.objects.count()
    open_tickets_count = Ticket.objects.filter(status='Open').count()
    in_progress_tickets_count = Ticket.objects.filter(status='In-Progress').count()
    resolved_tickets_count = Ticket.objects.filter(status='Resolved').count()

    context = {
        'tickets_count': tickets_count,
        'open_tickets_count': open_tickets_count,
        'in_progress_tickets_count': in_progress_tickets_count,
        'resolved_tickets_count': resolved_tickets_count,
        'page_title': 'Customer Supportive Dashboard',
    }
    return render(request, 'admin_template/admin_home.html', context)



@login_required
def profile_updates_admin(request):
    user = request.user
    profile = Profile.objects.get(user=user)  # This assumes a Profile exists for every user

    if request.method == 'POST':
        # Update user details
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.save()

        # Update profile details
        profile.mobile_number = request.POST.get('mobile_number')
        profile.save()

        messages.success(request, 'Profile updated successfully')
        return redirect('profile_updates_admin')  # Adjust the redirect URL as needed

    context = {
        'user': user,
        'profile': profile,
        'page_title': 'Admin Profile Updates'  # Add the page title here
    }
    return render(request, 'admin_template/profile_updates_admin.html', context)


from django.contrib import messages
from .models import Ticket, TicketStatus, TicketNote, TicketAttachment

@login_required
def manage_tickets_ad(request):
    query = request.GET.get('q')
    if query:
        tickets = Ticket.objects.filter(title__icontains=query)
    else:
        tickets = Ticket.objects.all()
        
    context = {
        'tickets': tickets,
        'page_title': 'Manage Tickets'
    }
    
    return render(request, 'admin_template/manage_tickets_admin.html', context)



import logging

logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ticket, TicketStatus, TicketNote
from .utils import send_ticket_notification  # Import the function

@login_required
def update_ticket_admin(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        note = request.POST.get('note', '')

        if status not in dict(Ticket.STATUS_CHOICES).keys():
            messages.error(request, 'Invalid status.')
            return redirect('manage_tickets_ad')

        ticket.status = status
        ticket.save()

        # Update or create TicketStatus
        ticket_status, created = TicketStatus.objects.get_or_create(ticket=ticket)
        ticket_status.note = note
        ticket_status.save()

        # Add note to TicketNote
        TicketNote.objects.create(ticket=ticket, user=request.user, note=note)

        # Send email notification
        sender_email = request.user.email
        recipient_email = ticket.user.email
        admin_email = request.user.email  # Assuming logged-in user is admin
        send_ticket_notification(ticket, note, admin_email)

        messages.success(request, 'Ticket updated successfully.')
        return redirect('manage_tickets_ad')

    notes = TicketNote.objects.filter(ticket=ticket).order_by('created_at')
    attachments = ticket.attachments.all()  # Get attachments

    context = {
        'ticket': ticket,
        'notes': notes,
        'attachments': attachments,
        'page_title': 'Update Ticket'
    }

    return render(request, 'admin_template/update_ticket_admin.html', context)



@login_required
def delete_note(request, note_id):
    note = get_object_or_404(TicketNote, id=note_id)
    ticket_id = note.ticket.id
    note.delete()

    return redirect('update_ticket_admin', ticket_id=ticket_id)



@login_required
def view_ticket_admin(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    attachments = ticket.attachments.all()
    ticket_status = TicketStatus.objects.filter(ticket=ticket).first()
    # Fetch all notes for the ticket
    notes = TicketNote.objects.filter(ticket=ticket).order_by('created_at')
    
    context = {
        'ticket': ticket,
        'attachments': attachments,
        'ticket_status': ticket_status,
        'notes': notes,
        'page_title': 'View Ticket'
    }

    return render(request, 'admin_template/view_ticket_admin.html', context)





#Staff_panel 
#-----------------------------------------------------------------------------------------------------------------------------

@login_required
def staff_home(request):
    user = request.user
    profile = Profile.objects.get(user=user)  # Fetch the user's profile
    
   
    open_tickets_count = Ticket.objects.filter(user=user, status='Open').count()
    in_progress_tickets_count = Ticket.objects.filter(user=user, status='In-Progress').count()
    resolved_tickets_count = Ticket.objects.filter(user=user, status='Resolved').count()

    context = {
        'user': user,
        'role': profile.role,
        'page_title': 'User Dashboard',
        'open_tickets_count': open_tickets_count,
        'in_progress_tickets_count': in_progress_tickets_count,
        'resolved_tickets_count': resolved_tickets_count,
    }

    return render(request, 'staff_template/staff_home.html', context)



@login_required
def profile_updates(request):
    user = request.user
    profile = Profile.objects.get(user=user)  # This assumes a Profile exists for every user

    if request.method == 'POST':
        # Update user details
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.save()

        # Update profile details
        profile.mobile_number = request.POST.get('mobile_number')
        profile.save()

        messages.success(request, 'Profile updated successfully')
        return redirect('profile_updates')

    context = {
        'user': user,
        'profile': profile,
        'page_title': 'Staff Profile Updates'
    }
    return render(request, 'staff_template/profile_updates.html', context)




from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Ticket, TicketAttachment


@login_required
def create_ticket(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        attachments = request.FILES.getlist('attachments')

        if not title or not description:
            messages.error(request, 'Title and Description are required.')
            return redirect('create_ticket')

        ticket = Ticket(title=title, description=description, user=request.user)  # Associate ticket with logged-in user
        ticket.save()

        for file in attachments:
            TicketAttachment.objects.create(ticket=ticket, file=file)

        messages.success(request, 'Ticket created successfully.')
        return redirect('manage_tickets')

    context = {
        'page_title': 'Create Ticket'
    }

    return render(request, 'staff_template/create_ticket.html', context)




@login_required
def manage_tickets(request):
    user = request.user
    tickets = Ticket.objects.filter(user=user)  # Filter tickets by logged-in user
    context = {
        'tickets': tickets,
        'page_title': 'Manage Tickets'
    }

    return render(request, 'staff_template/manage_tickets.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ticket, TicketNote
from .utils import send_ticket_notification  # Import the function

@login_required
def update_ticket(request, ticket_id):
    user = request.user
    ticket = get_object_or_404(Ticket, id=ticket_id, user=user)
    notes = TicketNote.objects.filter(ticket=ticket).order_by('created_at')
    attachments = ticket.attachments.all()  # Get attachments

    if request.method == 'POST':
        status = request.POST.get('status')
        note = request.POST.get('note', '')

        if status not in dict(Ticket.STATUS_CHOICES).keys():
            messages.error(request, 'Invalid status.')
            return redirect('update_ticket', ticket_id=ticket_id)

        ticket.status = status
        ticket.save()

        # Add note to TicketNote
        if note:
            TicketNote.objects.create(ticket=ticket, user=request.user, note=note)

        # Send email notification
        # sender_email = request.user.email
        # recipient_email = ticket.user.email
        # admin_email = request.user.email 
        # send_ticket_notification(ticket, note, admin_email)
        
        
        messages.success(request, 'Ticket updated successfully.')
        return redirect('manage_tickets')

    return render(request, 'staff_template/update_ticket.html', {
        'ticket': ticket,
        'notes': notes,
        'attachments': attachments,
        'page_title': 'Update Ticket'
    })



@login_required
def view_ticket(request, ticket_id):
    user = request.user
    ticket = get_object_or_404(Ticket, id=ticket_id, user=user)  # Ensure ticket belongs to the logged-in user
    attachments = ticket.attachments.all()
    notes = TicketNote.objects.filter(ticket=ticket).order_by('created_at')
    return render(request, 'staff_template/view_ticket.html', {
        'ticket': ticket,
        'attachments': attachments,
        'notes': notes,
        'page_title': 'View Ticket'
    })





#Customer_panel 
#-----------------------------------------------------------------------------------------------------------------------------


@login_required
def customer_home(request):
    user = request.user
    profile = Profile.objects.get(user=user)  # Fetch the user's profile
    
    context = {
        'user': user,
        'role': profile.role,
        'page_title': 'Customer Dashboard'
    }
    return render(request, 'customer_template/customer_home.html', context)




@login_required
def profile_updates_customer(request):
    user = request.user
    profile = Profile.objects.get(user=user)  # This assumes a Profile exists for every user

    if request.method == 'POST':
        # Update user details
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.save()

        # Update profile details
        profile.mobile_number = request.POST.get('mobile_number')
        profile.save()

        messages.success(request, 'Profile updated successfully')
        return redirect('profile_updates_customer')  # Make sure this matches your URL pattern name

    context = {
        'user': user,
        'profile': profile,
        'page_title': 'Customer Profile Updates'
    }
    return render(request, 'customer_template/profile_updates_customer.html', context)



@login_required
def customer_ticket_list(request):
    user = request.user
    tickets = Ticket.objects.all() 
    context = {
        'tickets': tickets,
        'page_title': 'My Tickets'
    }
    return render(request, 'customer_template/customer_ticket_list.html', context)



@login_required
def customer_ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)  # Get ticket by id
    attachments = TicketAttachment.objects.filter(ticket=ticket)
    notes = TicketNote.objects.filter(ticket=ticket).order_by('created_at')

    context = {
        'ticket': ticket,
        'attachments': attachments,
        'notes': notes,
        'page_title': 'Ticket Details'
    }
    return render(request, 'customer_template/customer_ticket_detail.html', context)










from django.contrib.auth import logout


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('Index_function')
