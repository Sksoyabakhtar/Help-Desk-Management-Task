from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Profile(models.Model):
    ROLE_CHOICES = (
        ('1', 'Staff'),
        ('2', 'Customer'),
        ('3', 'Admin')
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username

    @property
    def role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, 'Unknown')




from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In-Progress', 'In-Progress'),
        ('Resolved', 'Resolved'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tickets')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_tickets', default=1)


    def __str__(self):
        return self.title

    @property
    def color_class(self):
        now = timezone.now()
        time_diff = now - self.created_at
        print(f"Time difference for ticket {self.id}: {time_diff}")
        if self.status == 'Resolved':
            return 'table-success'
        elif self.status == 'Open' and time_diff > timedelta(days=2):
            return 'table-danger'
        else:
            return ''



class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.ticket.title}"
    
    

class TicketStatus(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Status for {self.ticket.title}"
    
    
    
class TicketNote(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.ticket.title} by {self.user.email}"
    
    
    
    
    
    
    
    
    