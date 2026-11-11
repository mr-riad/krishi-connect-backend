from .conftest import h


def listing(**kw):
    base = dict(crop_name="Boro Paddy", category="paddy", quantity=10, unit="mon", price_per_unit=1600,
                district="Khulna", upazila="Dumuria", harvest_date="2026-11-20", latitude=22.80, longitude=89.42)
    base.update(kw)
    return base


def test_auth_and_roles(client, users):
    assert client.get("/listings").status_code == 401
    # buyer cannot create listing, farmer cannot publish rate
    assert client.post("/listings", headers=h("buyer1"), json=listing()).status_code == 403
    r = dict(crop_name="Paddy", category="paddy", rate_per_unit=40, district="Khulna")
    assert client.post("/rates", headers=h("farmer1"), json=r).status_code == 403


def test_listing_crud_and_photos(client, users):
    r = client.post("/listings", headers=h("farmer1"), json=listing())
    assert r.status_code == 201, r.text
    lid = r.json()["id"]
    assert r.json()["quantity_kg"] == 400 and r.json()["price_per_kg"] == 40
    assert r.json()["farmer_phone"] == "+8801735678901"

    up = client.post(f"/listings/{lid}/photos", headers=h("farmer1"),
                     files=[("files", ("a.jpg", b"123", "image/jpeg"))])
    assert up.status_code == 200 and len(up.json()["photo_urls"]) == 1
    bad = client.post(f"/listings/{lid}/photos", headers=h("farmer1"),
                      files=[("files", ("a.pdf", b"123", "application/pdf"))])
    assert bad.status_code == 415

    assert client.patch(f"/listings/{lid}", headers=h("farmer2"), json={"quantity": 1}).status_code == 403
    p = client.patch(f"/listings/{lid}", headers=h("farmer1"), json={"price_per_unit": 2000})
    assert p.json()["price_per_kg"] == 50
    assert client.delete(f"/listings/{lid}", headers=h("farmer1")).status_code == 204
    assert client.get(f"/listings/{lid}", headers=h("buyer1")).status_code == 404


def test_search_filter_sort(client, users):
    client.post("/listings", headers=h("farmer1"), json=listing())  # 40/kg, 400kg, Khulna
    client.post("/listings", headers=h("farmer2"), json=listing(
        crop_name="Potato", category="vegetable", quantity=500, unit="kg", price_per_unit=25,
        district="Rajshahi", upazila=None, harvest_date="2026-12-05", latitude=24.37, longitude=88.60))
    client.post("/listings", headers=h("farmer1"), json=listing(
        crop_name="Onion", category="vegetable", quantity=1, unit="ton", price_per_unit=60000,
        district="khulna ", upazila=None, latitude=22.90, longitude=89.50, harvest_date="2026-11-01"))  # 60/kg

    def s(**params):
        r = client.get("/listings", headers=h("buyer1"), params=params)
        assert r.status_code == 200, r.text
        return [i["crop_name"] for i in r.json()["items"]]

    assert len(s()) == 3
    assert s(q="pota") == ["Potato"]
    assert sorted(s(category="vegetable")) == ["Onion", "Potato"]
    assert sorted(s(district="KHULNA")) == ["Boro Paddy", "Onion"]  # case/space-insensitive
    assert s(upazila="dumuria") == ["Boro Paddy"]
    assert s(min_price=30, max_price=50) == ["Boro Paddy"]
    assert s(min_quantity=450) == ["Potato", "Onion"] or sorted(s(min_quantity=450)) == ["Onion", "Potato"]
    assert s(harvest_from="2026-11-15", harvest_to="2026-11-30") == ["Boro Paddy"]
    assert s(sort="price_asc") == ["Potato", "Boro Paddy", "Onion"]
    assert s(sort="nearest", lat=22.81, lng=89.43)[0] == "Boro Paddy"
    assert s(lat=22.81, lng=89.43, radius_km=30, sort="nearest") == ["Boro Paddy", "Onion"]
    assert client.get("/listings", headers=h("buyer1"), params={"sort": "nearest"}).status_code == 400
    page = client.get("/listings", headers=h("buyer1"), params={"limit": 2, "offset": 2}).json()
    assert page["total"] == 3 and len(page["items"]) == 1


def test_rate_board_and_matching(client, users):
    lid = client.post("/listings", headers=h("farmer1"), json=listing()).json()["id"]
    r = dict(crop_name="Paddy", category="paddy", rate_per_unit=42, unit="kg", district="Khulna",
             demand_quantity=1000, latitude=22.82, longitude=89.55, valid_days=3)
    rate = client.post("/rates", headers=h("buyer1"), json=r)
    assert rate.status_code == 201, rate.text
    rid = rate.json()["id"]
    client.post("/rates", headers=h("buyer1"), json={**r, "crop_name": "Wheat", "category": "other", "district": "Dinajpur",
                                                   "latitude": 25.6, "longitude": 88.6})

    board = client.get("/rates", headers=h("farmer1"), params={"district": "khulna"}).json()
    assert board["total"] == 1
    near = client.get("/rates", headers=h("farmer1"), params={"lat": 22.8, "lng": 89.4, "sort": "nearest"}).json()
    assert near["items"][0]["crop_name"] == "Paddy"

    m = client.get(f"/rates/{rid}/matching-listings", headers=h("buyer1")).json()
    assert [x["id"] for x in m] == [lid]
    mr = client.get(f"/listings/{lid}/matching-rates", headers=h("farmer1")).json()
    assert [x["id"] for x in mr] == [rid]


def test_expired_rate_hidden(client, users):
    from app.deps import get_store
    from datetime import timedelta
    from app.utils import now
    r = client.post("/rates", headers=h("buyer1"), json=dict(crop_name="Paddy", category="paddy", rate_per_unit=40, district="Khulna")).json()
    get_store().update("rates", r["id"], {"expires_at": now() - timedelta(hours=1)})
    assert client.get("/rates", headers=h("farmer1")).json()["total"] == 0


def test_chat_flow(client, users):
    lid = client.post("/listings", headers=h("farmer1"), json=listing()).json()["id"]
    c = client.post("/chats", headers=h("buyer1"), json={"participant_id": "farmer1", "listing_id": lid})
    assert c.status_code == 200, c.text
    cid = c.json()["id"]
    assert client.post("/chats", headers=h("farmer1"), json={"participant_id": "buyer1"}).json()["id"] == cid
    assert client.post("/chats", headers=h("buyer1"), json={"participant_id": "buyer1"}).status_code == 400

    assert client.post(f"/chats/{cid}/messages", headers=h("buyer1"), json={"text": "Dam koto?"}).status_code == 201
    client.post(f"/chats/{cid}/messages", headers=h("buyer1"), json={"text": "  Ajke nibo  "})
    assert client.post(f"/chats/{cid}/messages", headers=h("buyer1"), json={"text": "   "}).status_code == 422

    farmer_view = client.get("/chats", headers=h("farmer1")).json()
    assert farmer_view[0]["unread_count"] == 2 and farmer_view[0]["last_message"] == "Ajke nibo"
    msgs = client.get(f"/chats/{cid}/messages", headers=h("farmer1")).json()
    assert [m["text"] for m in msgs] == ["Dam koto?", "Ajke nibo"]
    older = client.get(f"/chats/{cid}/messages", headers=h("farmer1"), params={"before": msgs[1]["created_at"]}).json()
    assert [m["text"] for m in older] == ["Dam koto?"]

    client.post(f"/chats/{cid}/read", headers=h("farmer1"))
    assert client.get("/chats", headers=h("farmer1")).json()[0]["unread_count"] == 0
    assert client.get(f"/chats/{cid}/messages", headers=h("farmer2")).status_code == 403


def test_call(client, users):
    r = client.post("/calls", headers=h("buyer1"), json={"target_uid": "farmer1"})
    assert r.status_code == 200 and r.json()["tel_uri"] == "tel:+8801735678901"
    assert client.post("/calls", headers=h("buyer1"), json={"target_uid": "nobody"}).status_code == 404
