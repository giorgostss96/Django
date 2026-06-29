from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth import login 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Booking
from datetime import datetime

def index(request):
    rooms = Room.objects.all()
    arrival = request.GET.get('arrival')
    departure = request.GET.get('departure')
    if arrival:
        print(f"Arrival date received: {arrival}")
    return render(request, 'bookings/index.html', {'rooms': rooms})

class UserSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)
def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'registration/signup.html', {'form': form})
    else:
        form = UserSignupForm()
    return render(request, 'registration/signup.html', {'form': form})

def room_list(request):
    room_type = request.GET.get('room_type')
    max_price = request.GET.get('max_price')
    arrival = request.GET.get('arrival')
    departure = request.GET.get('departure')
    occupied_rooms_ids = []
    if arrival and departure:
        try:
            date_format = '%Y-%m-%d'
            d1 = datetime.strptime(arrival, date_format)
            d2 = datetime.strptime(departure, date_format)
            if d2 <= d1:
                messages.error(request, "Η ημερομηνία αναχώρησης πρέπει να είναι μεταγενέστερη της άφιξης.")
                return redirect('index') 
            occupied_rooms_ids = Booking.objects.filter(
                status='active',
                check_in__lt=departure, 
                check_out__gt=arrival    
            ).values_list('room_id', flat=True)
        except ValueError:
            messages.error(request, "Μη έγκυρη μορφή ημερομηνίας.")
            return redirect('index')
    rooms = Room.objects.all()
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    if max_price:
        rooms = rooms.filter(price_per_night__lte=max_price)
    return render(request, 'bookings/rooms_list.html', {
    'rooms': rooms,
    'arrival': arrival,
    'departure': departure,
    'room_type': room_type,
    'max_price': max_price,
    'occupied_rooms_ids': occupied_rooms_ids,
     })

@login_required
def profile_view(request):
    my_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'bookings/profile.html', {
        'bookings': my_bookings
    })

def about(request):
    return render(request, 'bookings/about.html')

def blog(request):
    return render(request, 'bookings/blog.html')

@login_required
def make_booking(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        check_in_str = request.POST.get('check_in')
        check_out_str = request.POST.get('check_out')
        d1 = datetime.strptime(check_in_str, '%Y-%m-%d')
        d2 = datetime.strptime(check_out_str, '%Y-%m-%d')
        nights = (d2 - d1).days
        if nights <= 0:
            messages.error(request, "Η ημερομηνία αναχώρησης πρέπει να είναι μετά την άφιξη!")
            return render(request, 'bookings/booking_form.html', {
               'room': room,
               'arrival': check_in_str,
               'departure': check_out_str,
           })
        overlapping_bookings = Booking.objects.filter(
            room=room,
            status='active',
            check_in__lt=check_out_str,  
            check_out__gt=check_in_str   
        )
        if overlapping_bookings.exists():
            messages.error(request, "Δυστυχώς το δωμάτιο είναι ήδη κλεισμένο για αυτές τις ημερομηνίες.")
            return render(request, 'bookings/booking_form.html', {
                'room': room, 'arrival': check_in_str, 'departure': check_out_str,
            })
        total_price = nights * room.price_per_night
        Booking.objects.create(
            user=request.user,
            room=room,
            check_in=check_in_str,
            check_out=check_out_str,
            total_price=total_price, 
            status='active'
        )
        messages.success(request, f'Η κράτηση ολοκληρώθηκε! Συνολικό κόστος: {total_price}€')
        return redirect('index') 
    arrival = request.GET.get('arrival')
    departure = request.GET.get('departure')
    return render(request, 'bookings/booking_form.html', {
        'room': room,
        'arrival': arrival,
        'departure': departure,
    })

@login_required
def cancel_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        if booking.status == 'active':
            booking.status = 'cancelled' 
            booking.save()
            messages.success(request, "Η κράτηση ακυρώθηκε με επιτυχία.")
        else:
            messages.warning(request, "Η κράτηση είναι ήδη ακυρωμένη.")         
    return redirect('profile') 

def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'bookings/room_detail.html', {
        'room': room
    })