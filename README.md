# Virtual Teacher

A smart learning platform built with Django and Next.js that enables interactive learning through AI-powered conversations.

## Features

- User authentication (Learner, Teacher, Parent, Admin roles)
- Interactive AI conversations
- Real-time chat interface
- Role-based dashboards
- Conversation history
- Modern, responsive UI

## Tech Stack

### Backend
- Django
- Django REST Framework
- SQLite (development)

### Frontend
- Next.js 13+
- TypeScript
- Tailwind CSS
- React

## Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## Environment Variables

Create a `.env` file in the backend directory with the following variables:
```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 