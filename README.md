# twitter-content-scheduler

REST API for a Twitter/X content scheduler.

## Endpoints

Base path: `/v1`  
Interactive docs: `/docs` (Swagger UI), `/redoc`

Authentication

-   Initial sign-in: OAuth (Twitter/X) via `/v1/login` → `/v1/callback` (handled by utils.auth_utils).
-   Protected endpoints: JWT Bearer (validated by dependencies such as `CheckJwt()` and `get_current_active_user`).

Routes

-   GET /v1/login

    -   Description: Redirects the user to the Twitter/X OAuth authorization URL.
    -   Auth: none
    -   curl: `curl -i http://localhost:8000/v1/login`
    -   Response: 302/307 redirect to provider `Location: <auth_url>`

-   GET /v1/callback

    -   Description: OAuth callback. Exchanges code for access/refresh tokens and returns `Token`.
    -   Auth: none (called by provider)
    -   curl: `curl -i "http://localhost:8000/v1/callback?code=<code>&state=<state>"`
    -   Example response:
        ```json
        { "access_token": "...", "refresh_token": "...", "expires_in": 3600 }
        ```

-   GET /v1/profile

    -   Description: Return the current authenticated user's profile (`UserOut`).
    -   Auth: Bearer JWT
    -   curl: `curl -H "Authorization: Bearer <JWT>" http://localhost:8000/v1/profile`
    -   httpx (async):
        ```python
        import httpx, asyncio
        async def get_profile(jwt):
            async with httpx.AsyncClient() as c:
                r = await c.get("http://localhost:8000/v1/profile", headers={"Authorization": f"Bearer {jwt}"})
                return r.json()
        ```
    -   Example response:
        ```json
        { "id": 1, "username": "jdoe", "name": "John Doe" }
        ```

-   PUT /v1/profile

    -   Description: Update current user's profile (`BaseUser`).
    -   Auth: Bearer JWT
    -   curl:
        ```
        curl -X PUT -H "Authorization: Bearer <JWT>" -H "Content-Type: application/json" \
          -d '{"name":"New Name"}' http://localhost:8000/v1/profile
        ```

-   GET /v1/refresh

    -   Description: Exchange a refresh token (service handles specifics) for a new access token (`Token`).
    -   Auth: depends on refresh flow (see `get_new_access_token`)
    -   curl: `curl -H "Authorization: Bearer <REFRESH_TOKEN>" http://localhost:8000/v1/refresh`

-   POST /v1/logout

    -   Description: Revoke access/refresh tokens for the current user.
    -   Auth: Bearer JWT
    -   curl: `curl -X POST -H "Authorization: Bearer <JWT>" http://localhost:8000/v1/logout`
    -   Example response:
        ```json
        { "msg": "tokens revoked" }
        ```

-   GET /v1/get-post

    -   Description: Fetch user's tweets from X API. Uses `CheckJwt()` to get the user id and fetch OAuth from Redis. Returns the X API response.
    -   Auth: Bearer JWT
    -   curl: `curl -H "Authorization: Bearer <JWT>" http://localhost:8000/v1/get-post`
    -   Response: JSON returned by X API (tweets list)

-   GET /v1/posts/{post_id}

    -   Description: Retrieve a scheduled post (`PostOut`).
    -   Auth: Bearer JWT
    -   curl: `curl -H "Authorization: Bearer <JWT>" http://localhost:8000/v1/posts/123`
    -   Example response:
        ```json
        {
            "id": 123,
            "content": "Hello",
            "scheduled_at": "2025-12-18T10:00:00Z",
            "status": "PENDING"
        }
        ```

-   POST /v1/posts

    -   Description: Create a scheduled post (`BasePost`). Returns 201 Created.
    -   Auth: Bearer JWT
    -   curl:
        ```
        curl -X POST -H "Authorization: Bearer <JWT>" -H "Content-Type: application/json" \
          -d '{"content":"Hello","scheduled_at":"2025-12-18T10:00:00Z"}' http://localhost:8000/v1/posts
        ```

-   PUT /v1/posts/{post_id}
    -   Description: Update a pending scheduled post (cannot update sent or failed posts).
    -   Auth: Bearer JWT
    -   curl:
        ```
        curl -X PUT -H "Authorization: Bearer <JWT>" -H "Content-Type: application/json" \
          -d '{"content":"Updated content"}' http://localhost:8000/v1/posts/123
        ```

Notes

-   For exact request and response fields consult the Pydantic models in `models/` (e.g., `UserModel.py`, `TokenModel.py`, `PostModel.py`).
-   Error handling follows standard FastAPI patterns (HTTP status codes with JSON detail messages).
-   Protected endpoints rely on project dependencies (see `utils.dependencies.CheckJwt`, `services.user.get_current_active_user`).
