# 標準ライブラリ
from datetime import datetime, timedelta

# サードパーティ
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

# 自作モジュール
from auth_utils import hash_password, verify_password
from database import SessionLocal, engine
import models
import schemas

# JWT認証設定
SECRET_KEY = "demo_portfolio_secret_2026"  # 好きな文字列でOK, 今回はポートフォリオ用
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth認証スキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# FastAPI作成
app = FastAPI()

# DB初期化
models.Base.metadata.create_all(bind=engine)

# =============================
# DB
# =============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================
# Auth / JWT
# =============================
def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# ====================
# API機能
# ====================
# 一覧取得
@app.get("/todos", response_model=list[schemas.TodoResponse])
def get_todos(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Todo).filter(
        models.Todo.user_id == current_user.id
    ).all()

# 作成
@app.post("/todos", response_model=schemas.TodoResponse)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_todo = models.Todo(title=todo.title, done=todo.done, user_id=current_user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# 取得
@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.user_id == current_user.id
    ).first()
    
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return db_todo

# 更新
@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.user_id == current_user.id
    ).first()

    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db_todo.title = todo.title
    db_todo.done = todo.done
    db.commit()
    db.refresh(db_todo)
    return db_todo

# 削除
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.user_id == current_user.id
    ).first()

    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return {"message": "deleted"}

# ユーザー登録
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 既に存在するかチェック
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_pw = hash_password(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "user created"}

# ログイン
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
    
