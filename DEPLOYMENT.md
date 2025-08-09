# Deployment Guide

This project is designed for a **split deployment architecture**:
- **Backend (Django API)**: Deployed to AWS using Docker
- **Frontend (React)**: Deployed to Vercel

## Docker Files Overview

The project now contains only **2 Docker files**:

1. **`Dockerfile`** - Multi-stage build for Django backend only
2. **`docker-compose.yml`** - Backend services (Django + PostgreSQL + Redis + Celery)

## Local Development

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start backend services
docker-compose up -d

# 3. Start frontend separately (for development)
cd frontend
npm install
npm start
```

## AWS Deployment (Backend)

### Option 1: AWS EC2 with Docker Compose
```bash
# 1. Launch EC2 instance and install Docker
# 2. Clone repository
# 3. Create .env file with production values
# 4. Run services
docker-compose up -d
```

### Option 2: AWS ECS (Recommended for production)
```bash
# 1. Push Docker image to AWS ECR
# 2. Create ECS task definition using docker-compose.yml
# 3. Deploy to ECS cluster
```

### AWS Services Configuration:
- **Database**: Amazon RDS (PostgreSQL)
- **Cache**: Amazon ElastiCache (Redis)
- **Compute**: EC2 or ECS
- **Load Balancer**: Application Load Balancer

## Vercel Deployment (Frontend)

### Prerequisites
1. Push frontend code to GitHub
2. Connect GitHub repo to Vercel

### Environment Variables for Vercel:
```bash
REACT_APP_API_URL=https://your-aws-backend-url.com/api
```

### Deployment Steps:
1. **Connect Repository**: Link your GitHub repo to Vercel
2. **Configure Build**: 
   - Build Command: `cd frontend && npm run build`
   - Output Directory: `frontend/build`
3. **Set Environment Variables**: Add `REACT_APP_API_URL`
4. **Deploy**: Vercel will auto-deploy on push

## Environment Variables

### Backend (.env file):
```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgres://user:pass@rds-endpoint:5432/dbname
REDIS_URL=redis://elasticache-endpoint:6379/0
TWELVE_DATA_API_KEY=your-api-key
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ALLOWED_HOSTS=your-ec2-ip,your-domain.com
CORS_ALLOWED_ORIGINS=https://stock-price-alerting.vercel.app/
```

### Frontend (Vercel):
```bash
REACT_APP_API_URL=https://your-aws-backend.com/api
```

## Production Considerations

1. **Security**: Use AWS Secrets Manager for sensitive variables
2. **SSL**: Enable HTTPS on both AWS (Certificate Manager) and Vercel (automatic)
3. **Monitoring**: Use AWS CloudWatch for backend monitoring
4. **Scaling**: Configure ECS auto-scaling for backend services

## Development vs Production

- **Development**: Use docker-compose for full-stack local development
- **Production**: AWS backend + Vercel frontend for optimal performance and cost

This architecture provides:
- ✅ Separated concerns (API vs UI)
- ✅ Independent scaling
- ✅ Cost optimization
- ✅ Easy maintenance
