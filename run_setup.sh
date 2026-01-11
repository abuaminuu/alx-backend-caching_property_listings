# Make sure Docker is running
sudo systemctl start docker

# Run the setup script
./setup.sh

# Or run manually:
# docker-compose up -d
# pip install -r requirements.txt
# python manage.py makemigrations
# python manage.py migrate
# python manage.py createsuperuser
# python manage.py runserver
