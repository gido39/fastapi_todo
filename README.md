# FastAPI ToDo App

## 概要
JWT認証を用いたユーザー認証付きToDo管理APIです。  
FastAPIを用いてCRUD操作とユーザー認証を実装しています。

---

## 技術スタック
- Python
- FastAPI
- SQLAlchemy
- SQLite（ローカルDB）
- JWT（python-jose）

---

## 主な機能
- ユーザー登録
- ログイン（JWT発行）
- ToDoの作成・取得・更新・削除
- ユーザーごとのデータ分離

---

## 認証方式
JWT Bearer Tokenを使用  
Swagger UIのAuthorizeから認証可能

---

## API一覧
### 認証
- POST /register
- POST /login

### ToDo
- GET /todos
- POST /todos
- PUT /todos/{id}
- DELETE /todos/{id}

---

## 実行方法
```bash
uvicorn main:app --reload
```

```md id="r4"
http://127.0.0.1:8000/docs
```
