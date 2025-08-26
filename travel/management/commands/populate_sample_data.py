from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
import random
from travel.models import TravelOption
from travel.constants import TRAVEL_TYPES


class Command(BaseCommand):
    help = 'Populate sample travel data for Indian routes'

    def handle(self, *args, **options):
        # Clear existing data
        TravelOption.objects.all().delete()
        
        # Popular Indian routes
        routes = [
            ('Delhi', 'Mumbai'),
            ('Mumbai', 'Delhi'),
            ('Bangalore', 'Chennai'),
            ('Chennai', 'Bangalore'),
            ('Delhi', 'Bangalore'),
            ('Bangalore', 'Delhi'),
            ('Mumbai', 'Pune'),
            ('Pune', 'Mumbai'),
            ('Delhi', 'Jaipur'),
            ('Jaipur', 'Delhi'),
            ('Chennai', 'Hyderabad'),
            ('Hyderabad', 'Chennai'),
            ('Mumbai', 'Ahmedabad'),
            ('Ahmedabad', 'Mumbai'),
            ('Delhi', 'Chandigarh'),
            ('Chandigarh', 'Delhi'),
            ('Bangalore', 'Hyderabad'),
            ('Hyderabad', 'Bangalore'),
            ('Mumbai', 'Goa'),
            ('Goa', 'Mumbai'),
            ('Delhi', 'Lucknow'),
            ('Lucknow', 'Delhi'),
            ('Chennai', 'Kochi'),
            ('Kochi', 'Chennai'),
            ('Mumbai', 'Indore'),
            ('Indore', 'Mumbai'),
            ('Delhi', 'Amritsar'),
            ('Amritsar', 'Delhi'),
            ('Bangalore', 'Mysore'),
            ('Mysore', 'Bangalore'),
        ]

        # Airline/Railway/Bus operators
        operators = {
            'flight': ['IndiGo', 'SpiceJet', 'Air India', 'Vistara', 'GoFirst'],
            'train': ['Indian Railways', 'Rajdhani Express', 'Shatabdi Express', 'Duronto Express'],
            'bus': ['Redbus', 'KSRTC', 'MSRTC', 'Volvo', 'Private Operators']
        }

        # Base prices (in rupees)
        base_prices = {
            'flight': {'min': 2500, 'max': 8000},
            'train': {'min': 300, 'max': 2500},
            'bus': {'min': 200, 'max': 1500}
        }

        # Create travel options for the next 30 days
        created_count = 0
        for days_ahead in range(1, 31):  # Next 30 days
            travel_date = timezone.now() + timedelta(days=days_ahead)
            
            for source, destination in routes:
                # Create 1-3 options per route per day
                num_options = random.randint(1, 3)
                
                for _ in range(num_options):
                    travel_type = random.choice([t[0] for t in TRAVEL_TYPES])
                    
                    # Random departure time
                    hour = random.randint(6, 23)
                    minute = random.choice([0, 15, 30, 45])
                    departure_time = travel_date.replace(
                        hour=hour, 
                        minute=minute, 
                        second=0, 
                        microsecond=0
                    )
                    
                    # Calculate arrival time (add 1-8 hours for flights, 2-24 for trains, 4-16 for buses)
                    if travel_type == 'flight':
                        journey_hours = random.randint(1, 4)
                        journey_minutes = random.choice([0, 15, 30, 45])
                    elif travel_type == 'train':
                        journey_hours = random.randint(4, 24)
                        journey_minutes = random.choice([0, 15, 30])
                    else:  # bus
                        journey_hours = random.randint(4, 16)
                        journey_minutes = random.choice([0, 30])
                    
                    arrival_time = departure_time + timedelta(
                        hours=journey_hours, 
                        minutes=journey_minutes
                    )
                    
                    # Random price within range
                    price_range = base_prices[travel_type]
                    price = random.randint(price_range['min'], price_range['max'])
                    
                    # Random seats
                    if travel_type == 'flight':
                        total_seats = random.choice([150, 180, 200, 250])
                    elif travel_type == 'train':
                        total_seats = random.choice([200, 300, 500, 800])
                    else:  # bus
                        total_seats = random.choice([40, 45, 50, 55])
                    
                    available_seats = random.randint(
                        int(total_seats * 0.1),  # At least 10% available
                        int(total_seats * 0.9)   # At most 90% available
                    )
                    
                    # Random operator
                    operator = random.choice(operators[travel_type])
                    
                    # Service number
                    if travel_type == 'flight':
                        service_number = f"{operator[:2].upper()}-{random.randint(1000, 9999)}"
                    elif travel_type == 'train':
                        service_number = f"{random.randint(10000, 99999)}"
                    else:  # bus
                        service_number = f"BUS-{random.randint(1000, 9999)}"

                    travel_option = TravelOption.objects.create(
                        travel_type=travel_type,
                        source=source,
                        destination=destination,
                        departure_datetime=departure_time,
                        arrival_datetime=arrival_time,
                        price=price,
                        total_seats=total_seats,
                        available_seats=available_seats,
                        operator_name=operator,
                        service_number=service_number,
                        description=f"{travel_type.title()} service from {source} to {destination} operated by {operator}",
                    )
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} travel options for Indian routes!'
            )
        )
