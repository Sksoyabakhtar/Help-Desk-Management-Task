from django.core.mail import EmailMessage

def send_ticket_notification(ticket, note, admin_email):
    subject = f"Ticket Update: {ticket.title}"
    message = (f"Dear User,\n\n"
               f"Your ticket with the following details has been updated:\n\n"
               f"Title: {ticket.title}\n"
               f"Status: {ticket.status}\n"
               f"Note: {note}\n\n"
               f"Regards,\n"
               f"Support Team")

    recipient_email = ticket.user.email  # Email of the user who created the ticket

    email = EmailMessage(
        subject,
        message,
        'support@example.com',  # Fixed support email address for the sender
        [recipient_email],
        headers={'Reply-To': admin_email}  # Reply-To header set to the admin's email
    )

    try:
        email.send(fail_silently=False)
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
