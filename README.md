# Krishi Connect – Backend (Module 1)

FastAPI + Firebase (Firestore, Storage, Auth). Marketplace & Communication module.

## Features -> Endpoints
| Feature | Endpoints |
|---|---|
| 1. Farmer crop listing (+photos) | `POST /listings`, `POST /listings/{id}/photos`, `GET/PATCH/DELETE /listings/{id}`, `GET /listings/mine` |
| 2. Buyer rate board & location match | `POST /rates`, `GET /rates` (district/upazila/lat,lng), `GET /rates/{id}/matching-listings`, `GET /listings/{id}/matching-rates` |
| 3. Call & chat | `POST /calls`, `POST /chats`, `GET /chats`, `GET/POST /chats/{id}/messages`, `POST /chats/{id}/read` |
| 4. Search / filter / sort | `GET /listings?q=&category=&min_price=&max_price=&min_quantity=&max_quantity=&harvest_from=&harvest_to=&district=&upazila=&lat=&lng=&radius_km=&sort=newest\|price_asc\|nearest` |
| Profile | `GET/PUT /users/me` |

Interactive docs: http://localhost:8000/docs

## Setup (local, Firebase chhara)
```bash
cd krishi_backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
uvicorn app.main:app --reload
pytest                             # tests
```
Default `.env` = in-memory DB + `AUTH_DISABLED=true`. `/docs`-e **Authorize** e giye token hishebe
je kono uid likhun (e.g. `farmer1`), tarpor `PUT /users/me` diye role set korun:
`{"role":"farmer","name":"Nurul","phone":"01735678901","district":"Khulna"}`.

## Setup (Firebase – production)
1. Firebase Console -> Project settings -> **Service accounts** -> *Generate new private key* -> `serviceAccountKey.json` (project root-e rakhun, git-e dibenna).
2. Firebase Console -> **Storage** enable korun; bucket name copy korun (e.g. `krishi-xxx.firebasestorage.app`).
3. `.env`:
   ```
   USE_FIREBASE=true
   AUTH_DISABLED=false
   FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
   FIREBASE_STORAGE_BUCKET=<your-bucket>
   ```
4. `firestore.rules` file-er content Firebase Console -> Firestore -> Rules-e paste kore Publish korun.
5. `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Flutter-er sathe connect
- `lib/networks/endpoints.dart`-er `url` change korun: Android emulator -> `http://10.0.2.2:8000`, real device -> `http://<PC-IP>:8000`.
- Prottek request-e Firebase ID token pathan: `Authorization: Bearer ${await FirebaseAuth.instance.currentUser!.getIdToken()}`
  (project-er `DioSingleton.update(token)` already `Bearer` header set kore).
- Login-er por ekbar `PUT /users/me` call korun (name, district, upazila, lat/lng).
- **Real-time chat**: message pathate `POST /chats/{id}/messages`; live shunte Flutter-e Firestore snapshot:
  `FirebaseFirestore.instance.collection('conversations/$cid/messages').orderBy('created_at').snapshots()`
  (`cid` = duijon-er uid sorted kore `_` diye jora, ba `POST /chats` er response `id`).
- **Call**: `POST /calls {target_uid}` -> response-er `tel_uri` `call_helper.dart` diye launch korun.
- Photo: `POST /listings/{id}/photos` (multipart, field `files`, max 5, 5MB each).

## Notes / assumptions
- Unit conversion: 1 mon = 40 kg, 1 ton = 1000 kg, 1 bag = 50 kg. Price/quantity filter `price_per_kg` / `quantity_kg` diye hoy.
- Category keys: paddy, vegetable, fruit, pulse, spice, other.
- Filtering Python-e hoy (max 1000 active doc scan) – composite index lagena. Data onek boro hole Firestore GeoHash/Algolia dorkar hobe.
- Rate board-er `valid_days` shesh hole rate auto-hide hoy.
