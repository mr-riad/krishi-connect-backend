# 🌾 Krishi Connect — Full Backend API

A complete FastAPI + Firebase backend for the **Krishi Connect** agricultural mobile platform (Flutter).

---

## 📦 Project Structure

```
krishi_backend/
├── app/
│   ├── main.py                  # FastAPI app, all routers registered
│   ├── config.py                # Settings (env vars)
│   ├── deps.py                  # Auth middleware, DB/Storage deps
│   ├── schemas.py               # Core Pydantic models (listings, rates, chat, users)
│   ├── schemas_advisory.py      # Advisory, Machinery, News, Alerts, FCM schemas
│   ├── schemas_forum.py         # Community Forum schemas
│   ├── schemas_admin.py         # Admin panel schemas
│   ├── schemas_calendar.py      # Crop calendar schemas
│   ├── geo.py                   # Haversine distance helpers
│   ├── matching.py              # Crop/location matching logic
│   ├── storage.py               # Firebase Storage / Local file upload
│   ├── utils.py                 # Utilities (norm, now, phone format)
│   ├── db/
│   │   ├── base.py              # DocStore ABC
│   │   └── sqlite.py            # SQLite-backed document store (default)
│   ├── data/
│   │   └── crop_calendar.py     # Static crop calendar & intercrop data
│   └── routers/
│       ├── users.py             # /users
│       ├── listings.py          # /listings
│       ├── rates.py             # /rates
│       ├── chat.py              # /chats
│       ├── calls.py             # /calls
│       ├── calendar.py          # /calendar, /intercrop
│       ├── advisory.py          # /advisory/diseases, /advisory/tips
│       ├── machinery_news.py    # /machinery, /news
│       ├── forum.py             # /forum/posts, /forum/comments
│       ├── notifications.py     # /alerts/weather, /notifications/fcm/*
│       └── admin.py             # /admin/*
├── admin_panel/
│   └── index.html               # Admin dashboard (Bengali UI)
├── firestore.rules              # Firestore security rules
├── .env.example                 # Environment variable template
└── requirements.txt
```

---

## 🚀 Quick Start (Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy env file
cp .env.example .env
# Edit .env — set ADMIN_UIDS=admin123 (your test admin UID)

# 3. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **API Docs:** http://localhost:8000/docs
- **Admin Panel:** http://localhost:8000/admin-panel
- In dev mode, any Bearer token value is accepted as a UID.
- Use `Bearer admin123` as the Authorization header to test admin endpoints.

---

## 🔥 Firebase Setup (Production)

### 1. Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create project or use existing (`krishi-connect-9ca73`)
3. Enable: **Authentication** (Phone/OTP + Email), **Firestore**, **Cloud Storage**, **Cloud Messaging (FCM)**

### 2. Service Account Key
1. Project Settings → Service accounts → Generate new private key
2. Save as `serviceAccountKey.json` in the project root **OR** paste contents in `.env`

### 3. Environment Variables
```env
USE_FIREBASE=true
AUTH_DISABLED=false
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
# OR:
# FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
FIREBASE_STORAGE_BUCKET=krishi-connect-9ca73.firebasestorage.app
ADMIN_UIDS=uid_of_admin1,uid_of_admin2
```

### 4. Firestore Security Rules
Deploy the included `firestore.rules`:
```bash
firebase deploy --only firestore:rules
```

---

## 📲 Push Notifications (FCM)

### Flutter Setup
Add to `pubspec.yaml`:
```yaml
dependencies:
  firebase_core: latest
  firebase_messaging: latest
```

### Flutter: Register FCM Token
After login, call:
```dart
String? token = await FirebaseMessaging.instance.getToken();
await api.post('/notifications/fcm/register', {
  'token': token,
  'district': userDistrict,
  'platform': 'android',
});
```

### Topics
Devices are auto-subscribed to:
- `all_farmers` — everyone
- `district_{name}` — users in that district (e.g. `district_rajshahi`)

### Admin: Send Alerts
Use the Admin Panel → আবহাওয়া সতর্কতা or:
```
POST /alerts/weather
Authorization: Bearer <admin_token>
{
  "title_bn": "ভারী বৃষ্টির সতর্কতা",
  "message_bn": "আজ ভারী বৃষ্টির সম্ভাবনা। কাটা ফসল ঢেকে রাখুন।",
  "district": "রাজশাহী",
  "alert_type": "rain",
  "severity": "high"
}
```
This automatically broadcasts an FCM push to `district_rajshahi` topic.

---

## 🗂️ All API Endpoints (51 total)

### Module 1 — Marketplace & Communication
| Method | Path | Description |
|--------|------|-------------|
| GET/PUT | `/users/me` | Profile read/update |
| POST/GET | `/listings` | Create / search crop listings |
| GET | `/listings/mine` | My listings (farmer) |
| GET/PATCH/DELETE | `/listings/{id}` | Listing detail/edit/delete |
| POST | `/listings/{id}/photos` | Upload listing photos |
| GET | `/listings/{id}/matching-rates` | Matching buyer rates |
| POST/GET | `/rates` | Publish / browse buyer rate board |
| GET | `/rates/mine` | My rates (buyer) |
| GET/PATCH/DELETE | `/rates/{id}` | Rate detail/edit/delete |
| GET | `/rates/{id}/matching-listings` | Matching farmer listings |
| GET/POST | `/chats` | List / create conversations |
| GET/POST | `/chats/{cid}/messages` | Chat history / send message |
| POST | `/chats/{cid}/read` | Mark messages as read |
| POST | `/calls` | Trigger call (returns tel: URI) |

### Module 2 — Advisory & Info
| Method | Path | Description |
|--------|------|-------------|
| GET | `/calendar` | Full seasonal crop calendar |
| GET | `/calendar/season/{id}` | Season-specific calendar |
| GET | `/calendar/month/{n}` | Month-specific crops |
| GET | `/intercrop` | All intercropping guides |
| GET | `/intercrop/season/{id}` | Season-filtered intercrop guides |
| GET | `/intercrop/crop/{id}` | Crop-specific intercrop |
| GET | `/intercrop/companions/{id}` | Companion crops list |
| GET/POST | `/advisory/diseases` | List / create crop diseases |
| GET/PUT/DELETE | `/advisory/diseases/{id}` | Disease CRUD |
| GET/POST | `/advisory/tips` | List / create farming tips |
| GET/PUT/DELETE | `/advisory/tips/{id}` | Tip CRUD |
| GET/POST | `/machinery` | Machinery directory |
| GET/PUT/DELETE | `/machinery/{id}` | Machinery CRUD |
| GET/POST | `/news` | Ag-news / policy updates |
| GET/PUT/DELETE | `/news/{id}` | News CRUD |
| GET/POST | `/alerts/weather` | Active weather alerts + create |
| DELETE | `/alerts/weather/{id}` | Deactivate alert |
| POST | `/notifications/fcm/register` | Register device FCM token |
| POST | `/notifications/fcm/send` | Push to specific device |
| POST | `/notifications/fcm/send-topic` | Broadcast to topic |

### Module 3 — Community & Admin
| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/forum/posts` | List / create forum posts |
| GET/DELETE | `/forum/posts/{id}` | Post detail / delete |
| POST | `/forum/posts/{id}/media` | Upload media to post |
| POST | `/forum/posts/{id}/like` | Toggle like |
| GET/POST | `/forum/posts/{id}/comments` | Comments |
| DELETE | `/forum/comments/{id}` | Delete comment |
| POST | `/forum/posts/{id}/report` | Report a post |
| GET | `/admin/stats` | Platform analytics |
| GET | `/admin/users` | List all users |
| GET/PATCH/DELETE | `/admin/users/{uid}` | User management |
| GET | `/admin/listings` | All listings |
| PATCH/DELETE | `/admin/listings/{id}` | Moderate/delete listing |
| GET/PATCH | `/admin/reports` | Moderation reports |
| GET/DELETE | `/admin/forum/posts` | Forum moderation |

---

## 🔐 Security Notes

- In **production**, always set `AUTH_DISABLED=false` and `USE_FIREBASE=true`
- Admin role is granted to UIDs listed in `ADMIN_UIDS` env var
- All write endpoints require a valid Firebase Auth token
- Firestore Security Rules are layered on top — backend writes use Admin SDK (bypasses rules)

---

## 🛠️ Admin Panel

Open `http://localhost:8000/admin-panel` in your browser.

Features:
- 📊 Platform statistics dashboard
- 👥 User management (ban/unban/verify)
- 🌾 Listing moderation (approve/suspend/delete)
- 🚩 Spam report resolution
- 🦠 Disease database CRUD
- 💡 Farming tips management
- 🚜 Machinery directory
- 📰 Government news publishing
- 💬 Community forum moderation
- ⚠️ Weather alert creation & FCM broadcast
- 🔔 Manual push notification sender

Enter your Admin Bearer token and API base URL in the top-right corner.

---

## 🌐 Deployment (Render.com / Railway / Fly.io)

```bash
# Start command
uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Environment variables to set:
USE_FIREBASE=true
AUTH_DISABLED=false
FIREBASE_CREDENTIALS_JSON=<paste entire serviceAccountKey.json here>
FIREBASE_STORAGE_BUCKET=your-bucket.appspot.com
ADMIN_UIDS=uid1,uid2
CORS_ORIGINS=https://your-flutter-app.com,*
```
