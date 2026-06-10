# SideQuest

SideQuest is a Django REST Framework API for a small social platform where users share hobby and project updates, follow other profiles, like and comment on posts, and view a personalized feed. Moderators can remove inappropriate content and block accounts.

Deployment URL: `TODO`

## Technology Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite
- Gunicorn
- WhiteNoise

## Local Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run migrations:

```powershell
python manage.py migrate
```

Create reproducible demo data:

```powershell
python manage.py seed_demo
```

Run the development server:

```powershell
python manage.py runserver
```

## Demo Credentials

| Username | Password | Role |
|---|---|---|
| `user_demo` | `user12345` | standard user |
| `alice_demo` | `alice12345` | standard user |
| `bob_demo` | `bob12345` | standard user |
| `moderator_demo` | `moderator12345` | moderator |
| `admin_demo` | `admin12345` | admin/superuser |

## JWT Authentication

Login returns `access` and `refresh` tokens:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user_demo","password":"user12345"}'
```

Use the access token on protected endpoints:

```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Endpoints

| Method | URL | Auth | Role | Body | Purpose |
|---|---|---|---|---|---|
| POST | `/api/v1/auth/register/` | No | Anyone | `username`, `email`, `bio`, `password`, `password_confirm` | Register a standard user |
| POST | `/api/v1/auth/token/` | No | Anyone | `username`, `password` | Obtain JWT access and refresh tokens |
| POST | `/api/v1/auth/token/refresh/` | No | Anyone | `refresh` | Refresh an access token |
| GET | `/api/v1/auth/me/` | Yes | Active authenticated user | None | Return the current authenticated user |
| GET | `/api/v1/users/` | No | Anyone | None | List public user profiles |
| GET | `/api/v1/users/{id}/` | No | Anyone | None | Retrieve a public user profile |
| PATCH | `/api/v1/users/{id}/` | Yes | Profile owner only | `username`, `email`, `bio` | Update own profile |
| GET | `/api/v1/posts/` | No | Anyone | None | List posts |
| POST | `/api/v1/posts/` | Yes | Active authenticated user | `content` | Create a post |
| GET | `/api/v1/posts/{id}/` | No | Anyone | None | Retrieve a post |
| PATCH | `/api/v1/posts/{id}/` | Yes | Post owner only | `content` | Update own post |
| DELETE | `/api/v1/posts/{id}/` | Yes | Post owner or moderator | None | Delete a post |
| GET | `/api/v1/posts/{id}/comments/` | No | Anyone | None | List comments for a post |
| POST | `/api/v1/posts/{id}/comments/` | Yes | Active authenticated user | `content` | Create a comment |
| PATCH | `/api/v1/comments/{id}/` | Yes | Comment owner only | `content` | Update own comment |
| DELETE | `/api/v1/comments/{id}/` | Yes | Comment owner or moderator | None | Delete a comment |
| POST | `/api/v1/users/{id}/follow/` | Yes | Active authenticated user | None | Follow a user |
| DELETE | `/api/v1/users/{id}/unfollow/` | Yes | Active authenticated user | None | Unfollow a user |
| POST | `/api/v1/posts/{id}/like/` | Yes | Active authenticated user | None | Like a post |
| DELETE | `/api/v1/posts/{id}/unlike/` | Yes | Active authenticated user | None | Remove a like |
| GET | `/api/v1/feed/` | Yes | Authenticated user | None | List own posts and followed users' posts |
| POST | `/api/v1/moderation/users/{id}/block/` | Yes | Moderator only | None | Block an account |
| POST | `/api/v1/moderation/users/{id}/unblock/` | Yes | Moderator only | None | Unblock an account |

## Curl Examples

Register:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"new_demo","email":"new_demo@example.com","bio":"Building side quests.","password":"newpass12345","password_confirm":"newpass12345"}'
```

JWT login:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user_demo","password":"user12345"}'
```

Current user:

```bash
curl http://127.0.0.1:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Create a post:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Today I started a tiny but heroic side quest."}'
```

Create a comment:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/1/comments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"This deserves a quest marker."}'
```

Follow a user:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/2/follow/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Like a post:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/1/like/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Personalized feed:

```bash
curl http://127.0.0.1:8000/api/v1/feed/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Moderator block:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/moderation/users/3/block/ \
  -H "Authorization: Bearer MODERATOR_ACCESS_TOKEN"
```

Forbidden action example, normal user tries to block an account and receives `403`:

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/moderation/users/3/block/ \
  -H "Authorization: Bearer USER_ACCESS_TOKEN"
```

## Automated Tests

```powershell
python manage.py test
```

## Production Deployment

Required Django environment variables:

- `DJANGO_SECRET_KEY`: a strong secret value for production.
- `DJANGO_DEBUG`: set to `False`.
- `DJANGO_ALLOWED_HOSTS`: comma-separated hostnames, for example `sidequest.up.railway.app`.

Required Railway PostgreSQL variables:

```text
PGDATABASE=${{Postgres.PGDATABASE}}
PGUSER=${{Postgres.PGUSER}}
PGPASSWORD=${{Postgres.PGPASSWORD}}
PGHOST=${{Postgres.PGHOST}}
PGPORT=${{Postgres.PGPORT}}
```

Railway Pre-Deploy Command:

```bash
python manage.py migrate
```

Run `seed_demo` once after the first successful deployment, not on every deploy:

```bash
python manage.py seed_demo
```

Railway-style start command:

```bash
python manage.py collectstatic --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT
```
