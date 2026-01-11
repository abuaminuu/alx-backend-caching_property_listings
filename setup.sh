#!/bin/bash
# setup.sh

echo "Setting up Property Listings Project with Dockerized PostgreSQL and Redis..."

# Create required directories
mkdir -p postgres
mkdir -p static
mkdir -p media
mkdir -p templates

# Copy init.sql to postgres directory
cat > postgres/init.sql << 'EOF'
-- Initialize database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOF

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-$(openssl rand -base64 32)
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
POSTGRES_DB=property_db
POSTGRES_USER=property_user
POSTGRES_PASSWORD=property_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Settings
REDIS_HOST=redis
REDIS_PORT=6379

# Application Settings
TIME_ZONE=UTC
LANGUAGE_CODE=en-us
EOF
    echo ".env file created with generated secret key"
fi

# Start Docker containers
echo "Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>/dev/null || \
    echo "Superuser creation skipped (already exists or error)"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create sample data
echo "Creating sample properties..."
python manage.py shell << EOF
from properties.models import Property
from decimal import Decimal

# Create sample properties if none exist
if Property.objects.count() == 0:
    properties = [
        {
            'title': 'Modern Apartment Downtown',
            'description': 'Beautiful modern apartment in the heart of downtown with stunning city views.',
            'price': Decimal('350000'),
            'location': 'New York, NY',
            'property_type': 'apartment',
            'bedrooms': 2,
            'bathrooms': 2.0,
            'square_feet': 1200,
            'has_garage': True,
            'is_furnished': True,
        },
        {
            'title': 'Luxury Villa with Pool',
            'description': 'Spacious luxury villa with private pool and garden. Perfect for families.',
            'price': Decimal('850000'),
            'location': 'Miami, FL',
            'property_type': 'villa',
            'bedrooms': 4,
            'bathrooms': 3.5,
            'square_feet': 3200,
            'has_pool': True,
            'has_garden': True,
        },
        {
            'title': 'Cozy Cottage by the Lake',
            'description': 'Charming cottage with lake view. Peaceful and quiet neighborhood.',
            'price': Decimal('275000'),
            'location': 'Seattle, WA',
            'property_type': 'cottage',
            'bedrooms': 3,
            'bathrooms': 2.0,
            'square_feet': 1800,
            'has_garden': True,
        },
    ]
    
    for prop_data in properties:
        Property.objects.create(**prop_data)
    
    print(f"Created {len(properties)} sample properties")
else:
    print(f"Database already contains {Property.objects.count()} properties")
EOF

echo ""
echo "=========================================="
echo "🎉 Setup Complete!"
echo "=========================================="
echo ""
echo "Services running:"
echo "• Django App: http://localhost:8000"
echo "• Admin Panel: http://localhost:8000/admin"
echo "• PostgreSQL: localhost:5432"
echo "• Redis: localhost:6379"
echo "• pgAdmin: http://localhost:5050"
echo "• Redis Commander: http://localhost:8081"
echo ""
echo "Credentials:"
echo "• Database: property_user / property_password"
echo "• pgAdmin: admin@property.com / admin123"
echo ""
echo "Next steps:"
echo "1. Run: python manage.py runserver"
echo "2. Visit: http://localhost:8000/properties/"
echo "=========================================="
