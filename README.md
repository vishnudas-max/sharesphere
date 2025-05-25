ShareSphere

ShareSphere is a full-stack social media platform built with Django (backend) and React (frontend). It includes features such as authentication (including Google OAuth), real-time chat, stories, notifications, posts, payments, and more.

Tech Stack

- Backend: Django, Django REST Framework, Celery, Redis, Channels
- Frontend: React (in a separate repo)
- Database: PostgreSQL
- Authentication: Google OAuth2, JWT
- Asynchronous Tasks: Celery with Redis
- Real-Time Communication: Django Channels, WebSockets

Folder Structure (Backend)

sharesphere/
├── adminside/           - Admin-related views and logic
├── api/                 - API-level routing and config
├── chat/                - Real-time chat logic
├── googleauth/          - Google OAuth2 authentication logic
├── media/               - Media and file storage
├── notification/        - Notification system
├── payment/             - Payment verification and processing
├── post/                - Post creation, editing, deletion
├── sharesphere/         - Core project settings and URLs
├── story/               - Story feature logic
├── userside/            - User profile, follow/unfollow, etc.
├── manage.py
├── requirements.txt
└── .gitignore

Setup Instructions

1. Clone the Repository

git clone https://github.com/vishnudas-max/sharesphere.git

2. Create and Activate Virtual Environment

On Linux/macOS:

python3 -m venv venv
source venv/bin/activate
cd sharesphere

On Windows:

python -m venv venv
venv\Scripts\activate
cd sharesphere

3. Install Dependencies

pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file in the root of the project and add the following:

DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
REDIRECT_URI=http://localhost:8000/google/callback/

# Redis
REDIS_URL=redis://127.0.0.1:6379

# Email
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password

5. Apply Migrations and Create Superuser

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

Running the Project

1. Ensure Redis is Running

On Linux/macOS:

sudo service redis-server start

On Windows:

Download Redis for Windows from https://github.com/microsoftarchive/redis/releases

Then start Redis using:

redis-server

To test Redis is running:

redis-cli ping

(Output should be: PONG)

2. Run Celery

In a new terminal, with your virtual environment activated and inside the project folder:

celery -A sharesphere worker --pool=solo -l info

3. Run the Development Server

python manage.py runserver


Notes

- Redis must be running before you start Celery.
- Media files are stored in the /media/ directory.
- The React frontend is hosted separately.
- Google OAuth requires valid credentials from the Google Developer Console.
- Email features require valid SMTP credentials set in .env.

Contact

For support or questions:

- Email: vishnudask410@gmail.com
- Phone: +91 9207069066


