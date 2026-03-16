# Multi-tenant SaaS Application

A comprehensive multi-tenant SaaS application built with Python FastAPI, React, and PostgreSQL. Designed for B2B teams with strict tenant isolation, role-based access control, and subscription management.

## Features

### Core Features
- **Multi-tenant Architecture**: Strict tenant isolation using PostgreSQL Row Level Security (RLS)
- **Role-based Access Control**: Owner, Admin, Member, and Viewer roles with granular permissions
- **Authentication & Authorization**: JWT-based auth with refresh tokens and SSO support
- **File Management**: Secure file uploads with S3 integration and storage limits
- **Project Management**: Organize work with projects and file associations
- **User Management**: Invite and manage team members within tenants
- **Audit Logging**: Comprehensive activity tracking and compliance
- **Subscription Management**: Stripe integration with Basic and Pro plans

### Technical Features
- **Backend**: FastAPI with SQLAlchemy ORM and Alembic migrations
- **Frontend**: React with Material-UI and TypeScript
- **Database**: PostgreSQL with Row Level Security for tenant isolation
- **File Storage**: AWS S3 integration with presigned URLs
- **Payments**: Stripe integration for subscription management
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Docker**: Containerized application with Docker Compose
- **Security**: Rate limiting, CORS, and security headers

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   FastAPI       │    │   PostgreSQL    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Material-UI   │    │   SQLAlchemy    │    │   Row Level     │
│   Components    │    │   ORM           │    │   Security      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   AWS S3        │
                       │   (File Storage)│
                       └─────────────────┘
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multi-tenant-saas
   ```

2. **Set up environment variables**
   ```bash
   cp backend/env.example backend/.env
   # Edit backend/.env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Database Setup**
   ```bash
   # Start PostgreSQL
   docker run -d --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15
   
   # Run migrations
   cd backend
   alembic upgrade head
   ```

## Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/multitenant_saas

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
S3_BUCKET_NAME=your-s3-bucket-name

# Stripe
STRIPE_SECRET_KEY=sk_test_your-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## API Documentation

The API is fully documented with OpenAPI/Swagger. Access the interactive documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/tenants/` - Get tenant information
- `GET /api/v1/projects/` - List projects
- `POST /api/v1/files/upload` - Upload files
- `GET /api/v1/audit/` - Get audit logs

## Database Schema

### Core Tables
- **tenants**: Organization/tenant information
- **users**: User accounts and authentication
- **memberships**: User-tenant relationships with roles
- **projects**: Tenant projects
- **files**: File metadata and storage information
- **audit_logs**: Activity tracking and compliance

### Row Level Security
All tenant-related tables have RLS policies that automatically filter data based on the current tenant context, ensuring complete data isolation.

## Subscription Plans

### Basic Plan - $29/month
- 5 team members
- 1 GB storage
- Basic features
- Email support

### Pro Plan - $99/month
- 50 team members
- 50 GB storage
- Advanced features
- Priority support
- SSO integration
- Custom integrations

## Security Features

- **Tenant Isolation**: PostgreSQL RLS ensures complete data separation
- **JWT Authentication**: Secure token-based authentication
- **Role-based Access**: Granular permissions based on user roles
- **Rate Limiting**: API rate limiting to prevent abuse
- **Audit Logging**: Comprehensive activity tracking
- **File Security**: Secure file uploads with access controls
- **CORS Protection**: Configured CORS policies
- **Security Headers**: XSS, CSRF, and other security headers

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting
cd backend
flake8 app/
black app/
isort app/

# Frontend linting
cd frontend
npm run lint
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Deployment

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment
The application is designed to be deployed on any cloud provider:
- AWS (ECS, EKS, Lambda)
- Google Cloud (GKE, Cloud Run)
- Azure (Container Instances, AKS)
- DigitalOcean (App Platform)

## Monitoring and Observability

- **Health Checks**: Built-in health check endpoints
- **Audit Logs**: Comprehensive activity tracking
- **Error Handling**: Structured error responses
- **Logging**: Structured logging with different levels

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Note:  Showcase for Demo Portfolioi Project.

## Author: Ravinder Singh
