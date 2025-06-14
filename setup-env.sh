#!/bin/bash

echo "🚀 Setting up environment files for Virtual Teacher Platform"
echo ""

# Frontend setup
echo "📱 Setting up Frontend environment..."
if [ ! -f "frontend/.env.local" ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
    echo "✅ Created frontend/.env.local"
else
    echo "⚠️  frontend/.env.local already exists"
fi

# Backend setup
echo "🔧 Setting up Backend environment..."
if [ ! -f "backend/.env" ]; then
    cat > backend/.env << EOF
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-this
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
EOF
    echo "✅ Created backend/.env"
else
    echo "⚠️  backend/.env already exists"
fi

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update the SECRET_KEY in backend/.env"
echo "2. Update the TOGETHER_API_KEY in backend/.env"
echo "3. Update database credentials if needed"
echo "4. For production, update FRONTEND_URL and NEXT_PUBLIC_API_URL"
echo ""
echo "🔗 See README.md for detailed instructions" 