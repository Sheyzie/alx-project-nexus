# Project Nexus

## Overview 

This case study focuses on creating a backend for a Job Board Platform. The backend facilitates job postings, role-based access control, and efficient job search features. It integrates advanced database optimization and comprehensive API documentation.

## Project Goals
The primary objectives of the job board backend are:

### API Development

- Build APIs for managing job postings, categories, and applications.

### Access Control

- Implement role-based access control for admins and users.

### Database Efficiency

- Optimize job search with advanced query indexing.

## Technologies

| Technology | Purpose                                           |
| ---------- | ------------------------------------------------- |
| Django     | High-level Python framework for rapid development |
| PostgreSQL | Database for storing job board data               |
| JWT        | Secure role-based authentication                  |
| Swagger    | API endpoint documentation                        |

## Key Features

### Job Posting Management

- APIs for creating, updating, deleting, and retrieving job postings.

- Categorize jobs by industry, location, and type.

### Role-Based Authentication

- Admins can manage jobs and categories.

- Users can apply for jobs and manage applications.

### Optimized Job Search

- Use indexing and optimized queries for efficient job filtering.

- Implement location-based and category-based filtering.

### API Documentation

- Use Swagger for detailed API documentation.

- Host documentation at `/api/docs` for frontend integration.

## Database Design Entities

1. **User**

- `id`: UUID / bigserial PK (use `UUIDField(primary_key=True, default=uuid4)`).

- `email`: varchar, unique, indexed (Django: `EmailField(unique=True)`).

- `password`: varchar (hashed) (`CharField`).

- `is_active`: boolean (default=True).

- `is_staff`: boolean (for Django admin).

- `role`: varchar (choices: `admin`, `employer`, `recruiter`, `candidate`) — Role-based access.

- `date_joined`: timestamp with timezone (`DateTimeField(auto_now_add=True)`).

- `last_login`: timestamp (`DateTimeField(null=True)`).

- `social_auth_provider`: varchar, nullable.

- `is_verified`: boolean (email confirmed).

- `created_at`: timestam (`DATETIMEFIELD(auto_now_add=True)`)


**Relationships:**

- One-to-one with `Profile`.

- One-to-many with `Application` (user applies to many jobs).

- One-to-many with `Bookmark`.

**Indexes:**

- Unique index on email.

- Index on role for filtering by role.

2. **Profile**

- `id`: PK (separate with OneToOne).

- `user`: OneToOneField to `User` (on_delete=CASCADE).

- `full_name`: varchar.

- `headline`: varchar (short tagline).

- `bio`: text.

- `phone_number`: varchar (nullable).

- `location`: foreign key to `Location`.

- `resume_url`: text (link to uploaded resume).

- `skills`: ManyToMany -> `Skill`.

- `visibility`: enum (public/private).

**Relationship:**
- One-to-one with `Location`.
- Many-to-many with `Skill`.

**Indexes:**

- Index on `user_id`.

- Consider GIN index on `skills` array.

3) **Company**

- `id`: UUID PK.

- `name`: varchar, indexed.

- `slug`: varchar, unique.

- `description`: text.

- `website`: varchar.

- `logo_url`: text.

- `location`: FK to `Location`.

- `created_by`: FK to `User` (who created company record).

- `verified`: boolean.

**Relationships:**

- Company (1) → (N) Job

**Indexes:**

- Index on `name` and `slug`

4) **Job**

- `id`: UUID PK.

- `title`: varchar (indexed, used in full-text).

- `slug`: varchar, unique (human URL).

- `description`: text (long) — full-text searchable.

- `company`: FK -> `Company` (nullable if posted by user).

- `posted_by`: FK -> `User` (`employer/admin`).

- `status`: enum {`draft`, `published`, `archived`, `closed`}.

- `employment_type`: enum {`full_time`, `part_time`, `contract`, `internship`, `temporary`, `remote`}.

- `salary_min`: integer (nullable).

- `salary_max`: integer (nullable).

- `currency`: varchar (e.g., `USD`, `NGN`).

- `location`: FK -> `Location`

- `is_remote`: boolean.

- `is_featured`: boolean.

- `application_deadline`: date (nullable).

- `created_at`: timestamp (auto_now_add).

- `updated_at`: timestamp (auto_now).

**Relationships:**

Job (1) → (N) `Application`

Job (M) ↔ (M) `Category` (via Job.categories)

Job (M) ↔ (M) `Skill` (via Job.skills)

Job (1) → (N) `Attachment`


**Indexes:**

- Primary: `id`.

- B-tree index on `created_at`, `status`, `employment_type`.

- Full-text (GIN) index on `title`, `description` (tsvector).

- GIN trigram index on `title` for fuzzy search (pg_trgm).

- Index on `company_id`.

- Index on `location_id`.

- Composite index for filtering (e.g., (`status`, `employment_type`, `location_id`)).

**Optimization:**

- Use PostgreSQL `tsvector` column for full-text search and GIN index.

- Use PostGIS `geometry(Point,4326)` for job_location_point if you want distance queries and radius search (requires `postgis` extension).

- Alternatively store `latitude` and `longitude` columns and index with `cube` + `earthdistance` or GiST on `point`.

5. **Category**

- `id`: PK.

- `name`: varchar, unique.

- `slug`: varchar, unique.

- `description`: text (nullable).

- `parent`: FK self-referential (nullable) — supports hierarchical categories (industry -> sub-industry).

**Relationships:**

- `Category` (M) <--> (M) Job

**Indexes:**

- `Unique` index on `slug`, `name`.

- `Index` on `parent_id`.

6. **Skill**

- `id`: PK.

- `name`: varchar, unique.

- `slug`: varchar, unique.

**Relationships:**

- `Skill` (M) ↔ (M) `Job`

- `Skill` (M) ↔ (M) `Profile`

**Indexes:**

- Unique on `name`

7. **Application**

- `id`: UUID PK.

- `job`: FK -> `Job` (on_delete=CASCADE).

- `applicant`: FK -> `User` (on_delete=SET_NULL / CASCADE) — applicant user account.

- `cover_letter`: text (nullable).

- `resume_url`: text (nullable) — candidate resume snapshot.

- `status`: enum {`applied`, `reviewed`, `shortlisted`, `interviewed`, `offered`, `rejected`, `withdrawn`}.

- `applied_at`: timestamp (auto_now_add).

- `updated_at`: timestamp (auto_now).

- `source`: enum/string (e.g., `UI`, `email`, `referral`).

- `notes`: text (private recruiter notes).

**Indexes**

- Index on (`job_id`, `applicant_id`) unique to prevent duplicate applications (or create unique constraint).

- Index on `status`, `applied_at`.

8. **JobCategory (join table)**

- `id`: PK.

- `job`: FK -> `Job`.

- `category`: FK -> `Category`.

Indexes

- Unique composite index (`job_id`, `category_id`).

9. **JobSkill (join table)**

- `id`: PK.

- `job`: FK -> `Job`.

- `skill`: FK -> `Skill`.

- `proficiency_level`: enum (optional).

Indexes

- Unique (`job_id`, `skill_id`).

10. **Location**

- `id`: PK.

- `country`: varchar.

- `region/state`: varchar.

- `city`: varchar.

- `postal_code`: varchar.

- `address_line`: varchar.

- `latitude`: decimal(9,6).

- `longitude`: decimal(9,6).

- `point`: PostGIS `geometry(Point,4326)` (recommended for distance queries).

**Relationships:**

- `Location` (1) -> (N) `Job`

- Company may reference Location

**Indexes:**

- GiST index on `point` if using PostGIS.

- B-tree on `city`, `country` for filtering.

11. **Attachment**

- `id`: PK.

- `job`: FK -> `Job` (nullable if attachment belongs to application/profile).

- `application`: FK -> `Application` (nullable).

- `uploader`: FK -> `User`.

- `file_url`: text.

- `file_type`: varchar.

- `created_at`: timestamp.

**Indexes**

- Index on `job_id`, `application_id`.

### Relationships

- `User (1) — (1) Profile`

- `User (1) — (N) Job (posted_by)`

- `Company (1) — (N) Job`

- `Job (1) — (N) Application`

- `User (1) — (N) Application (applicant)`

- `Job (M) — (M) Category via join table`

- `Job (M) — (M) Skill via join table`

- `User (1) — (N) Bookmark`

- `Job (1) — (N) Attachment`

- `Location (1) — (N) Job`



