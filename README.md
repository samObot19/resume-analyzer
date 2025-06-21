# Resume Analyzer - n8n-Driven AI-Powered System

A secure, AI-powered resume analysis system that uses FastAPI backend, n8n automation, OpenAI analysis, and PostgreSQL storage.

## 🧠 Project Overview

This system provides:
- **Secure API endpoints** with JWT authentication
- **PDF resume upload** and processing
- **AI-powered information extraction** using OpenAI
- **Automated workflow** orchestrated by n8n
- **Structured data storage** in PostgreSQL
- **Dockerized deployment** for easy setup

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│   FastAPI   │───▶│     n8n     │───▶│ PostgreSQL  │
│             │    │   Backend   │    │  Workflow   │    │  Database   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │                    │
                          ▼                    ▼
                   ┌─────────────┐    ┌─────────────┐
                   │   File      │    │   OpenAI    │
                   │   Storage   │    │   Analysis  │
                   └─────────────┘    └─────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### 1. Clone and Setup
```bash
git clone <repository-url>
cd resume-analyzer
```

### 2. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your OpenAI API key
nano .env
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `SECRET_KEY`: JWT secret key (change in production)

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Access Services
- **FastAPI Backend**: http://localhost:8000
- **n8n Interface**: http://localhost:5678 (admin/admin123)
- **pgAdmin**: http://localhost:5050 (admin@example.com/admin123)
- **PostgreSQL**: localhost:5432

## 🔐 Authentication

### Default Credentials
- **Username**: `admin`
- **Password**: `admin123`

### Getting JWT Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

## 📡 API Endpoints

### Authentication
- `POST /auth/login` - Get JWT token (unsecured)

### Resume Upload
- `POST /upload` - Upload PDF resume (requires JWT)

### Health Check
- `GET /health` - Service health status

### Example Usage

#### Upload Resume
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@resume.pdf"
```

Response:
```json
{
  "message": "Resume uploaded successfully",
  "filename": "resume.pdf",
  "file_path": "/app/uploads/uuid_resume.pdf",
  "webhook_status": {
    "status": "success",
    "message": "File uploaded and processing started"
  }
}
```

## 🔄 n8n Workflow

The n8n workflow automatically processes uploaded resumes:

1. **Webhook Trigger** - Receives file information from FastAPI
2. **Text Extraction** - Extracts text from PDF using pdf-parse
3. **OpenAI Analysis** - Analyzes resume content using GPT-3.5-turbo
4. **Data Parsing** - Structures extracted information
5. **Database Storage** - Saves to PostgreSQL
6. **Response** - Returns processing results

### Workflow Setup
1. Access n8n at http://localhost:5678
2. Login with admin/admin123
3. Import the workflow from `workflows/resume_workflow.json`
4. Configure OpenAI credentials in n8n
5. Activate the workflow

## 🗄️ Database Schema

```sql
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    skills TEXT[],
    experience_years FLOAT,
    last_job_title TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Sample Data
```sql
SELECT * FROM resumes;
```

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| backend | 8000 | FastAPI application |
| n8n | 5678 | Automation platform |
| postgres | 5432 | Database |
| pgadmin | 5050 | Database management |

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: JWT secret key
- `OPENAI_API_KEY`: OpenAI API key
- `N8N_WEBHOOK_URL`: n8n webhook endpoint
- `POSTGRES_*`: Database configuration

### Volume Mounts
- `./backend/uploads`: Resume file storage
- `./workflows`: n8n workflow definitions
- `postgres_data`: Database persistence
- `n8n_data`: n8n configuration persistence

## 🧪 Testing

### 1. Test Authentication
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 2. Test Upload (with JWT)
```bash
# Get token first
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Upload resume
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_resume.pdf"
```

### 3. Check Database
```bash
# Connect to PostgreSQL
docker exec -it resume-analyzer-postgres psql -U postgres -d resume_analyzer

# Query results
SELECT * FROM resumes ORDER BY uploaded_at DESC;
```

## 🚨 Security Considerations

1. **Change default passwords** in production
2. **Use strong SECRET_KEY** for JWT
3. **Configure CORS** appropriately
4. **Secure file uploads** with validation
5. **Use HTTPS** in production
6. **Regular security updates**

## 🐛 Troubleshooting

### Common Issues

1. **n8n not starting**
   - Check if port 5678 is available
   - Verify environment variables

2. **Database connection issues**
   - Ensure PostgreSQL container is running
   - Check network connectivity

3. **File upload failures**
   - Verify upload directory permissions
   - Check file size limits

4. **OpenAI API errors**
   - Verify API key is correct
   - Check API quota and billing

### Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs n8n
docker-compose logs postgres
```

## 📝 Development

### Local Development
```bash
# Start only dependencies
docker-compose up postgres n8n -d

# Run backend locally
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Adding New Features
1. Modify FastAPI endpoints in `backend/`
2. Update n8n workflow in `workflows/`
3. Test with Docker Compose
4. Update documentation

## 📄 License

This project is for educational and testing purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: This is a test project for evaluating n8n automation skills, FastAPI development, and AI integration capabilities.
