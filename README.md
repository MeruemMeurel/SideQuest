# SideQuest

SideQuest is a Django REST Framework API for a small social platform where users share hobby and project updates, follow other profiles, like and comment on posts, and view a personalized feed. Moderators can remove inappropriate content and block accounts.

- Student: Manuel Mauro 7135710
- Project Type: REST API
- Framework: Django + Django REST Framework
- Track: Social Media API
- Deployment URL: https://sidequest-social.up.railway.app

## Technology Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite for local evaluation
- PostgreSQL for Railway deployment
- Gunicorn
- WhiteNoise

## Features by Role

- Public users: list posts, retrieve posts, list public profiles, retrieve public profiles, list comments.
- Authenticated standard users: register, log in with JWT, manage own profile, create/update/delete own posts, comment, follow/unfollow users, like/unlike posts, view personalized feed.
- Moderators: delete inappropriate posts or comments and block/unblock accounts.
- Admin: access Django administration.

## Database Strategy

SQLite is used locally. The populated `db.sqlite3` file is included in the repository for evaluation and already contains realistic demo data and working demo accounts.

Railway uses PostgreSQL in production through the Railway-provided `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST`, and `PGPORT` environment variables.

## Local Setup

Clone the repository:

```powershell
git clone https://github.com/MeruemMeurel/SideQuest
cd SideQuest
```

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

The included `db.sqlite3` already contains demo data. To recreate or refresh it, run the idempotent seed command:

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

| Method | URL | Auth | Role | Body | Purpose | Expected Response |
|---|---|---|---|---|---|---|
| POST | `/api/v1/auth/register/` | No | Anyone | `username`, `email`, `bio`, `password`, `password_confirm` | Register a standard user | `201 + created object`, `400 on invalid input` |
| POST | `/api/v1/auth/token/` | No | Anyone | `username`, `password` | Obtain JWT access and refresh tokens | `200 + access/refresh`, `401 on bad credentials` |
| POST | `/api/v1/auth/token/refresh/` | No | Anyone | `refresh` | Refresh an access token | `200 + access`, `401 on invalid token` |
| GET | `/api/v1/auth/me/` | Yes | Active authenticated user | None | Return the current authenticated user | `200 + JSON object`, `401 without authentication` |
| GET | `/api/v1/users/` | No | Anyone | None | List public user profiles | `200 + JSON list` |
| GET | `/api/v1/users/{id}/` | No | Anyone | None | Retrieve a public user profile | `200 + JSON object`, `404 if missing` |
| PATCH | `/api/v1/users/{id}/` | Yes | Profile owner only | `username`, `email`, `bio` | Update own profile | `200 + updated object`, `401 without authentication`, `403 when permission is missing` |
| GET | `/api/v1/posts/` | No | Anyone | None | List posts | `200 + JSON list` |
| POST | `/api/v1/posts/` | Yes | Active authenticated user | `content` | Create a post | `201 + created object`, `400 on invalid content`, `401 without authentication` |
| GET | `/api/v1/posts/{id}/` | No | Anyone | None | Retrieve a post | `200 + JSON object`, `404 if missing` |
| PATCH | `/api/v1/posts/{id}/` | Yes | Post owner only | `content` | Update own post | `200 + updated object`, `403 when permission is missing`, `400 on invalid content` |
| DELETE | `/api/v1/posts/{id}/` | Yes | Post owner or moderator | None | Delete a post | `204 No Content`, `403 when permission is missing` |
| GET | `/api/v1/posts/{id}/comments/` | No | Anyone | None | List comments for a post | `200 + JSON list` |
| POST | `/api/v1/posts/{id}/comments/` | Yes | Active authenticated user | `content` | Create a comment | `201 + created object`, `400 on invalid content`, `401 without authentication` |
| PATCH | `/api/v1/comments/{id}/` | Yes | Comment owner only | `content` | Update own comment | `200 + updated object`, `403 when permission is missing`, `400 on invalid content` |
| DELETE | `/api/v1/comments/{id}/` | Yes | Comment owner or moderator | None | Delete a comment | `204 No Content`, `403 when permission is missing` |
| POST | `/api/v1/users/{id}/follow/` | Yes | Active authenticated user | None | Follow a user | `201 + created object`, `400 on invalid or duplicate action`, `401 without authentication` |
| DELETE | `/api/v1/users/{id}/unfollow/` | Yes | Active authenticated user | None | Unfollow a user | `204 No Content`, `404 if not following` |
| POST | `/api/v1/posts/{id}/like/` | Yes | Active authenticated user | None | Like a post | `201 + created object`, `400 on duplicate action`, `401 without authentication` |
| DELETE | `/api/v1/posts/{id}/unlike/` | Yes | Active authenticated user | None | Remove a like | `204 No Content`, `404 if not liked` |
| GET | `/api/v1/feed/` | Yes | Authenticated user | None | List own posts and followed users' posts | `200 + JSON list`, `401 without authentication` |
| POST | `/api/v1/moderation/users/{id}/block/` | Yes | Moderator only | None | Block an account | `200 + JSON object`, `403 when permission is missing`, `400 when blocking self` |
| POST | `/api/v1/moderation/users/{id}/unblock/` | Yes | Moderator only | None | Unblock an account | `200 + JSON object`, `403 when permission is missing` |

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

## Reproducible Testing Workflow

For local testing:

```bash
BASE_URL=http://127.0.0.1:8000
```

The same commands work online by changing the base URL:

```bash
BASE_URL=https://sidequest-social.up.railway.app
```

> Note: some interaction commands may return `400 Bad Request` if the demo relationship or like already exists. Run `python manage.py seed_demo` to restore the reproducible demo state before repeating the full workflow.

Call the public post list:

```bash
curl -i "$BASE_URL/api/v1/posts/"
```

Log in as `alice_demo` and store the access token automatically:

```bash
ALICE_TOKEN=$(curl -s -X POST "$BASE_URL/api/v1/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_demo","password":"alice12345"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access'])")
```

Call `/api/v1/auth/me/`:

```bash
curl -i "$BASE_URL/api/v1/auth/me/" \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

Create a post and store `POST_ID` automatically:

```bash
POST_ID=$(curl -s -X POST "$BASE_URL/api/v1/posts/" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Documented a side quest and left breadcrumbs for the evaluator."}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

Patch the created post:

```bash
curl -i -X PATCH "$BASE_URL/api/v1/posts/$POST_ID/" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Updated side quest: the breadcrumbs now have labels."}'
```

Follow another user:

```bash
curl -i -X POST "$BASE_URL/api/v1/users/1/follow/" \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

Like a post:

```bash
curl -i -X POST "$BASE_URL/api/v1/posts/1/like/" \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

Create a comment:

```bash
curl -i -X POST "$BASE_URL/api/v1/posts/1/comments/" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"This quest has excellent documentation energy."}'
```

View the personalized feed:

```bash
curl -i "$BASE_URL/api/v1/feed/" \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

Delete the created post:

```bash
curl -i -X DELETE "$BASE_URL/api/v1/posts/$POST_ID/" \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

Demonstrate a forbidden moderator action attempted by a standard user. Expected result: HTTP `403`.

```bash
curl -i -X POST "$BASE_URL/api/v1/moderation/users/3/block/" \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

Log in as `moderator_demo` and demonstrate a permitted moderation action:

```bash
MOD_TOKEN=$(curl -s -X POST "$BASE_URL/api/v1/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"moderator_demo","password":"moderator12345"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access'])")

curl -i -X POST "$BASE_URL/api/v1/moderation/users/3/block/" \
  -H "Authorization: Bearer $MOD_TOKEN"

curl -i -X POST "$BASE_URL/api/v1/moderation/users/3/unblock/" \
  -H "Authorization: Bearer $MOD_TOKEN"
```

## Expected Responses

- Successful JWT login: HTTP `200` with `access` and `refresh`.
- Valid creation: HTTP `201` with the created object.
- Successful deletion: HTTP `204 No Content`.
- Unauthenticated protected request: HTTP `401`.
- Forbidden action: HTTP `403`.
- Invalid content: HTTP `400`.

## Interactive API Documentation

Swagger UI:

`https://sidequest-social.up.railway.app/api/docs/`

ReDoc:

`https://sidequest-social.up.railway.app/api/redoc/`

OpenAPI schema:

`https://sidequest-social.up.railway.app/api/schema/`

Swagger UI allows endpoint testing directly from the browser. For protected endpoints, obtain an access token from `/api/v1/auth/token/`, click **Authorize**, and enter the access token.

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
