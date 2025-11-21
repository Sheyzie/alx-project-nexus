# Project Nexus (Job Platform Backend)

## Overview 

A scalable job board backend built with Django REST Framework, GraphQL, PostgreSQL, Docker, JWT Authentication, and Role-Based Access Control.
The platform provides APIs for job postings, applications, companies, user accounts, and locations, with optimized search, UUID-based primary keys, and CI/CD with GitHub Actions and Render.

## Features

### Core Features

1. User registration, authentication, and JWT-based login.

2. Role-based access control for Admins, Recruiters, and Applicants.

3. Company management (creation, update, verification flow).

4. Job posting CRUD operations with UUID primary keys.

5. Job search with filters for location, industry, type, and experience.

6. Job applications with per-user validation and ownership protection.

7. Location service using django-location-field with geocoding.

8. GraphQL schema for queries and mutations.

9. Docker support for development and deployment.

10. CI/CD pipeline using GitHub Actions, Docker, and Render.

### Technical Features

- Django 5.2 and Python 3.12.

- PostgreSQL database with UUID primary keys.

- Swagger/OpenAPI documentation available at /api/docs.

- Pagination, throttling, and permission classes integrated.

- pytest-based test suite covering all endpoints.

- Modular architecture following domain-driven design (users, jobs, companies, locations, applications).

## Installation and Setup

### Prerequisites

- Python 3.12 or later

- Docker and Docker Compose

- PostgreSQL 14+ (optional if not using Docker)

1. **Clone Repository**

```bash
git clone https://github.com/Sheyzie/alx-project-nexus
cd alx-project-nexus/job_platform_app
```

2. **Environment Variables**

Create a `.env` file:

```ini
# django config
DEBUG=false # <--- set to true during production
SECRET_KEY= 'django_super_secret'

# db config
POSTGRES_DB=your_db
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_very_secure_password
POSTGRES_HOST=db # <--- set to localhost/your_host if your not running via docker 
POSTGRES_PORT=5432

# hosts and cors
ALLOWED_HOSTS=your_host
CORS_ALLOW_ALL_ORIGINS=True
```

#### Local Development

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Run Migrations**

```bash
python manage.py migrate
```

3. **Start Development Server**

```bash
python manage.py runserver
```

#### Docker Setup

```bash
docker-compose up --build
```

## API Routes

### Authentication

| Method | Endpoint           | Description               |
| ------ | ------------------ | ------------------------- |
| POST   | /api/v1/users/register | Create account            |
| POST   | /api/v1/users/login    | Login with JWT            |
| GET    | /api/v1/users/profile  | Get authenticated profile |

#### Users

| Method | Endpoint                      | Description                 |
| ------ | ----------------------------- | --------------------------- |
| GET    | /api/v1/users                    | List all users (admin only) |
| GET    | /api/v1/users/[uuid:pk](uuid:pk) | Retrieve user               |
| PATCH  | /api/v1/users/[uuid:pk](uuid:pk) | Update user                 |

#### Companies

| Method | Endpoint                          | Description                    |
| ------ | --------------------------------- | ------------------------------ |
| GET    | /api/v1/companies                    | List companies                 |
| POST   | /api/v1/companies                    | Create company (authenticated) |
| GET    | /api/v1/companies/[uuid:pk](uuid:pk) | Retrieve company               |
| PATCH  | /api/v1/companies/[uuid:pk](uuid:pk) | Update company                 |

#### Jobs

| Method | Endpoint                     | Description                  |
| ------ | ---------------------------- | ---------------------------- |
| GET    | /api/v1/jobs                    | List jobs with filters       |
| POST   | /api/v1/jobs                    | Create job (admin/recruiter) |
| GET    | /api/v1/jobs/[uuid:pk](uuid:pk) | Retrieve job details         |
| PATCH  | /api/v1/jobs/[uuid:pk](uuid:pk) | Update job                   |
| DELETE | /api/v1/jobs/[uuid:pk](uuid:pk) | Delete job                   |

#### Applications

| Method | Endpoint                             | Description           |
| ------ | ------------------------------------ | --------------------- |
| GET    | /api/v1/applications                    | List all applications |
| POST   | /api/v1/applications                    | Apply for job         |
| GET    | /api/v1/applications/[uuid:pk](uuid:pk) | Retrieve application  |
| DELETE | /api/v1/applications/[uuid:pk](uuid:pk) | Withdraw application  |

#### Locations

| Method | Endpoint       | Description    |
| ------ | -------------- | -------------- |
| GET    | /api/v1/locations | List locations |
| POST   | /api/v1/locations | Add location   |


#### GraphQL

| Type                | Endpoint    |
| ------------------- | ----------- |
| GraphQL API         | /graphql    |
| GraphiQL Playground | /playground |

## Technologies

- Django 5.2

- Django REST Framework

- GraphQL (Graphene)

- PostgreSQL

- Docker and Docker Compose

- JWT Authentication

- GitHub Actions CI/CD

- django-location-field

## Project Structure

```plaintext
.
├── docs
│   └── job_platform_erd.drawio.png
├── job_platform_app
│   ├── applications
│   ├── common
│   ├── companies
│   ├── jobs
│   ├── locations
│   ├── users
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── job_platform
│   ├── manage.py
│   ├── templates
│   └── requirements.txt
└── README.md
```

## Running Tests

```bash
python manage.py test
```

### Tests cover:

- Users and authentication

- Job CRUD operations

- Applications

- Companies

- Locations

- GraphQL queries and mutations

## Deployment (CI/CD)

The project supports a full CI/CD pipeline using:

1. GitHub Actions

2. Docker Build and Push

3. Render automatic deploy

Pipeline includes:

- Tests

- Deployment trigger

Full configuration lives in `.github/workflows/ci-cd.yml.`

## Contribution Guide

1. Create a feature branch.

2. Run tests before submitting pull request.

3. Ensure code follows PEP8.

4. Update documentation when adding new features.
