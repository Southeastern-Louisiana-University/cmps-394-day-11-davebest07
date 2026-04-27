from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from keycloak import KeycloakOpenID

app = FastAPI()
security = HTTPBearer()

keycloak_openid = KeycloakOpenID(
    server_url="http://keycloak:8080/",
    client_id="myclient",
    realm_name="myrealm",
)

@app.get("/health")
def health():
    return {"status": "ok"}

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token_info = keycloak_openid.decode_token(
            token.credentials,
            options={"verify_aud": False}
        )
        return token_info
    except Exception as e:
        print(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/protected-resource")
def protected_route(user: dict = Depends(get_current_user)):
    return {
        "message": "You have accessed a protected resource",
        "user_id": user.get("sub"),
        "username": user.get("preferred_username")
    }
