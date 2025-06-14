# Virtual Teacher Platform

An interactive learning platform that connects teachers, students, and parents in a virtual educational environment.

## Features

- User Authentication with role-based access (Learner, Teacher, Parent, Admin)
- Real-time AI-powered chat interactions
- Grade-specific content for learners
- Modern, responsive UI built with Next.js and Tailwind CSS
- Secure backend API with Django REST Framework

## Tech Stack

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- React

### Backend
- Django 4.x
- Django REST Framework
- PostgreSQL
- Python 3.x

## Setup Instructions

### Quick Setup (Recommended)

Run the setup script to automatically create environment files:

**On Windows:**
```bash
setup-env.bat
```

**On macOS/Linux:**
```bash
chmod +x setup-env.sh
./setup-env.sh
```

### Manual Setup

### Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Create environment file:
```bash
# Create .env file in backend directory
cp .env.example .env  # If .env.example exists
# Or create .env manually with the following variables:
```

**Backend Environment Variables (.env):**
```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000

# Database Settings
PGDATABASE=virtual_teacher
PGUSER=vteacher_user
PGPASSWORD=password
PGHOST=localhost
PGPORT=5432

# AI API Settings
TOGETHER_API_KEY=your-together-api-key-here
TOGETHER_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create environment file:
```bash
# Create .env.local file in frontend directory
```

**Frontend Environment Variables (.env.local):**
```bash
# API Base URL - Change this for different environments
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm run dev
```

## Environment-Specific Configuration

### Local Development
- **Frontend**: Uses `http://localhost:8000` for API calls
- **Backend**: Allows CORS from `http://localhost:3000`

### Production Deployment
- **Frontend**: Set `NEXT_PUBLIC_API_URL` to your production API URL
- **Backend**: Set `FRONTEND_URL` to your production frontend URL

**Example Production Environment Variables:**

Frontend (.env.production):
```bash
NEXT_PUBLIC_API_URL=https://your-production-api.com
```

Backend (.env):
```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
FRONTEND_URL=https://your-production-frontend.com
ADDITIONAL_CORS_ORIGINS=https://your-production-frontend.com
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 