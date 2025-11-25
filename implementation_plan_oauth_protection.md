# OAuth2 Protection Implementation Plan

## Goal
Secure all API endpoints in `roles` and `users` modules using OAuth2 with Bearer token authentication.

## Proposed Changes

### 1. Protect Role Endpoints
#### [MODIFY] [roles.py](file:///e:/INSTITUTE/institute_lms/center_admin/app/api/v1/endpoints/roles.py)
- Import `deps` from `app.api`.
- Import `Usuario` from `app.models.models`.
- Add `current_user: Usuario = Depends(deps.get_current_user)` dependency to the following endpoints:
    - `create_role`
    - `read_roles`
    - `read_role`
    - `update_role`
    - `delete_role`

### 2. Protect User Endpoints
#### [MODIFY] [users.py](file:///e:/INSTITUTE/institute_lms/center_admin/app/api/v1/endpoints/users.py)
- Ensure `deps` and `Usuario` are imported (already present).
- Add `current_user: Usuario = Depends(deps.get_current_user)` dependency to the remaining endpoints:
    - `create_user`
    - `read_user`
    - `update_user`
    - `delete_user`
    - (Note: `read_users` is already protected)

## Verification
- Verify that accessing these endpoints without a token returns `401 Unauthorized`.
- Verify that accessing these endpoints with a valid token works as expected.
