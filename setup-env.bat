@echo off
echo 🚀 Setting up environment files for Virtual Teacher Platform
echo.

REM Frontend setup
echo 📱 Setting up Frontend environment...
if not exist "frontend\.env.local" (
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 > frontend\.env.local
    echo ✅ Created frontend\.env.local
) else (
    echo ⚠️  frontend\.env.local already exists
)

REM Backend setup
echo 🔧 Setting up Backend environment...
if not exist "backend\.env" (
    (
        echo # Django Settings
        echo DEBUG=True
        echo SECRET_KEY=your-secret-key-here-change-this
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo.
        echo # Frontend URL for CORS
        echo FRONTEND_URL=http://localhost:3000
        echo.
        echo # Database Settings
        echo PGDATABASE=virtual_teacher
        echo PGUSER=vteacher_user
        echo PGPASSWORD=password
        echo PGHOST=localhost
        echo PGPORT=5432
        echo.
        echo # AI API Settings
        echo TOGETHER_API_KEY=your-together-api-key-here
        echo TOGETHER_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1
    ) > backend\.env
    echo ✅ Created backend\.env
) else (
    echo ⚠️  backend\.env already exists
)

echo.
echo 🎉 Environment setup complete!
echo.
echo 📝 Next steps:
echo 1. Update the SECRET_KEY in backend\.env
echo 2. Update the TOGETHER_API_KEY in backend\.env
echo 3. Update database credentials if needed
echo 4. For production, update FRONTEND_URL and NEXT_PUBLIC_API_URL
echo.
echo 🔗 See README.md for detailed instructions
pause 