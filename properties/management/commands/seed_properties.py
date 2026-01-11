# properties/management/commands/seed_properties.py
from django.core.management.base import BaseCommand
from properties.models import Property
from decimal import Decimal
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Seed database with sample properties'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of properties to create'
        )
    
    def handle(self, *args, **options):
        fake = Faker()
        count = options['count']
        
        property_types = ['house', 'apartment', 'condo', 'townhouse', 'villa', 'cottage']
        locations = [
            'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
            'Miami, FL', 'Seattle, WA', 'Boston, MA', 'Denver, CO',
            'Atlanta, GA', 'Phoenix, AZ'
        ]
        
        self.stdout.write(f"Creating {count} sample properties...")
        
        properties_created = 0
        for i in range(count):
            try:
                property_data = {
                    'title': f"{fake.word().title()} {random.choice(['House', 'Apartment', 'Villa', 'Condo'])}",
                    'description': fake.text(max_nb_chars=200),
                    'price': Decimal(random.randrange(100000, 1000000, 50000)),
                    'location': random.choice(locations),
                    'property_type': random.choice(property_types),
                    'bedrooms': random.randint(1, 5),
                    'bathrooms': Decimal(random.randrange(10, 35)) / 10,  # 1.0 to 3.5
                    'square_feet': random.randrange(800, 4000, 100),
                    'has_garage': random.choice([True, False]),
                    'has_pool': random.choice([True, False]),
                    'has_garden': random.choice([True, False]),
                    'is_furnished': random.choice([True, False]),
                    'status': random.choice(['available', 'available', 'available', 'sold', 'pending']),
                }
                
                Property.objects.create(**property_data)
                properties_created += 1
                
                if properties_created % 10 == 0:
                    self.stdout.write(f"Created {properties_created} properties...")
                    
            except Exception as e:
                self.stderr.write(f"Error creating property: {e}")
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {properties_created} properties!")
        )
