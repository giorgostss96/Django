from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    ROOM_TYPES = (
        ('single', 'Μονόκλινο'),
        ('double', 'Δίκλινο'),
        ('suite', 'Σουίτα'),
    )
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.get_room_type_display()} - {self.price_per_night}€"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('active', 'Ενεργή'),
        ('cancelled', 'Ακυρώθηκε'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Κράτηση {self.id} από {self.user.username}"
