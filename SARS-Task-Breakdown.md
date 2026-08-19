# Smart ATM Routing System (SARS) — Task Breakdown (4 People) — v2

                                                                                          |
| ----------- | ---------------------------------------------------------------------------------------------------------- |
| **عبدالله** | Infra + Project Config + `accounts/` (Auth & RBAC) + 🆕 `kiosk/` scaffold + SCR-01                         |
| **محمد**    | `atms/` (ATM model, heartbeat, transaction attempt, WebSocket, network-stats) + 🆕 `kiosk/` SCR-05, SCR-06 |
| **سارة**    | `routing/` (Routing Engine) + `notifications/` (SMS)                                                       |
| **صفية**    | `frontend/` (Admin Dashboard) بالكامل + 🆕 `kiosk/` SCR-02, SCR-03, SCR-04                                 |

### توزيع شاشات الـ Kiosk (نهائي)

الشاشات البسيطة اتوزعت على اللي هيخلصوا الـ backend بتاعهم بدري، وصفية أخدت الشاشات اللي فيها منطق أعقد (reasons متعددة، عرض بدائل) عشان تفضل مركزة على الـ Admin Dashboard:

| الشاشة                         | المسؤول     | السبب                                  |
| ------------------------------ | ----------- | -------------------------------------- |
| SCR-01 (اختيار الخدمة والمبلغ) | **عبدالله** | شاشة إدخال بسيطة، مفيهاش منطق شرطي     |
| SCR-02 (فحص الحالة)            | **صفية**    | مرتبطة بمنطق الـ timeout والـ 3 ثواني  |
| SCR-03 (غير متاحة)             | **صفية**    | فيها 4 حالات مختلفة حسب `reason`       |
| SCR-04 (اختيار بديل)           | **صفية**    | عرض بيانات ديناميكية من الـ API        |
| SCR-05 (رقم الموبايل)          | **محمد**    | شاشة إدخال بسيطة + شرط مسح الرقم فورًا |
| SCR-06 (تأكيد)                 | **محمد**    | شاشة نجاح ثابتة، مفيهاش منطق           |

> **عبدالله** كمان مسؤول عن الأساسيات المشتركة لتطبيق الـ kiosk (`package.json`, `Dockerfile`, `.env.example`, `sessionSlice.js`, `services/api.js`) — لازم يخلصها قبل ما محمد وصفية يقدروا يبدأوا شاشاتهم، فهي أولوية بعد ما يخلص `accounts/`.

### ترتيب الاعتماديات (مين ينتظر مين)

1. **عبدالله** يخلص `sars_core/` (settings) + `common/` + `accounts/` الأول — الكل بيعتمد عليهم (settings, permissions, error format).
2. **محمد** يخلص الـ `ATM` model الأول في `atms/models.py` — لأن **سارة** محتاجاه في الـ Routing Engine، وصفية محتاجة شكل الـ response بتاعه.
3. **سارة** و**صفية** يقدروا يشتغلوا بالتوازي بعد كده، وبيتفقوا على شكل الـ JSON responses من الـ API Contract (كله موثق، محدش محتاج يستني التاني فعليًا).
4. **عبدالله** بعد ما يخلص `accounts/`، يعمل الـ scaffold المشترك بتاع `kiosk/` (package.json, Dockerfile, sessionSlice.js, services/api.js) — **محمد وصفية مينفعش يبدأوا شاشاتهم في الـ kiosk قبل كده**.
5. بعد الـ scaffold، **محمد** و**صفية** يقدروا يبنوا شاشاتهم في الـ kiosk بالتوازي مع باقي شغلهم.

---

## 👤 عبدالله — Infra + Config + Auth

### `.gitignore`

- [ ] استبعد: `venv/`, `__pycache__/`, `*.pyc`, `node_modules/`, `.env`, `dist/`, `build/`, `.DS_Store`, `*.sqlite3`, `media/`

### `.env.example` (روت المشروع)

- [ ] لو فيه متغيرات مشتركة بين backend/frontend (زي `COMPOSE_PROJECT_NAME`) حطها هنا، غير كده سيبه فاضي مع تعليق بيوجه لـ `backend/.env.example` و`frontend/.env.example`

### `docker-compose.yml`

- [ ] Service `db`: postgres (postgis image عشان `current_cash_balance`/lat-lng، استخدم `postgis/postgis`)
- [ ] Service `redis`: للـ Celery broker وقناة الـ WebSocket
- [ ] Service `backend`: build من `./backend`, يعتمد على `db` و`redis`, يشغل `runserver` أو `daphne` (لأننا محتاجين ASGI للـ WebSocket)
- [ ] Service `celery`: نفس الـ image بتاع backend، بس الأمر `celery -A sars_core worker -l info`
- [ ] Service `frontend`: build من `./frontend`, يعمل proxy لـ `backend` على المنفذ بتاع الـ API
- [ ] اربط `volumes` للكود عشان الـ hot reload وقت التطوير

### `README.md`

- [ ] وصف مختصر للمشروع (من الـ Overview بتاع المستند)
- [ ] خطوات التشغيل: `docker-compose up`، ازاي تعمل migration، ازاي تعمل superuser
- [ ] رابط لـ `docs/api-contract.md` و`docs/diagrams/`
- [ ] جدول بالـ apps الأربعة ومين مسؤول عن إيه (ينفعك تلزق التوزيع ده كله)

### `.github/workflows/backend-ci.yml`

- [ ] Trigger: `push`/`pull_request` على `backend/**`
- [ ] Steps: checkout → setup Python → `pip install -r requirements.txt -r requirements-dev.txt` → `flake8` أو `ruff` → `pytest`

### `.github/workflows/frontend-ci.yml`

- [ ] Trigger: `push`/`pull_request` على `frontend/**`
- [ ] Steps: checkout → setup Node → `npm ci` → `npm run lint` → `npm test`

---

### `backend/sars_core/settings/base.py`

- [ ] `INSTALLED_APPS`: أضف `rest_framework`, `channels`, `accounts`, `atms`, `routing`, `notifications`, `common`
- [ ] `DATABASES`: اقرأ من env vars (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`)
- [ ] `REST_FRAMEWORK`: حط `DEFAULT_AUTHENTICATION_CLASSES` فاضية هنا (كل app هيحدد الـ auth بتاعه لوحده — API Key للـ ATM endpoints، JWT للـ Admin endpoints)
- [ ] `CHANNEL_LAYERS`: استخدم `channels_redis` مربوط بـ `REDIS_URL`
- [ ] `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND`: من `REDIS_URL`

### `backend/sars_core/settings/dev.py` / `prod.py`

- [ ] `dev.py`: `DEBUG=True`, `ALLOWED_HOSTS=["*"]`, يستورد من `base.py`
- [ ] `prod.py`: `DEBUG=False`, `ALLOWED_HOSTS` من env، إعدادات أمان إضافية (`SECURE_SSL_REDIRECT`, إلخ)

### `backend/sars_core/celery.py`

- [ ] إعداد تطبيق Celery قياسي (`app = Celery("sars_core")`)، `app.config_from_object("django.conf:settings", namespace="CELERY")`, `app.autodiscover_tasks()`

### `backend/sars_core/asgi.py`

- [ ] اربط `ProtocolTypeRouter` بين `http` (Django views العادية) و`websocket` (URLRouter بتاع `atms/consumers.py` — هتلاقيه من محمد)

### `backend/manage.py` / `Dockerfile` / `requirements.txt` / `requirements-dev.txt` / `pytest.ini`

- [ ] `requirements.txt`: `django`, `djangorestframework`, `channels`, `channels-redis`, `celery`, `redis`, `psycopg2-binary`, `djangorestframework-simplejwt`, `requests` (لـ Google Maps/Twilio)
- [ ] `requirements-dev.txt`: `pytest`, `pytest-django`, `pytest-cov`, `flake8` أو `ruff`
- [ ] `Dockerfile`: base `python:3.12-slim`، `pip install`، `CMD` يشغل daphne (مش runserver عادي، عشان WebSocket)
- [ ] `pytest.ini`: `DJANGO_SETTINGS_MODULE = sars_core.settings.dev`

### `backend/.env.example`

- [ ] `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- [ ] `REDIS_URL`
- [ ] `JWT_SECRET`
- [ ] `GOOGLE_MAPS_API_KEY`
- [ ] `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`
- [ ] `ATM_API_KEY_SALT` (لتوليد/فحص API keys بتاعة الماكينات)

---

### `backend/accounts/models.py`

- [ ] Model `Admin` (أو extend `AbstractUser`): `admin_id` (PK/UUID), `username`, `password_hash`, `role` (choices: `ADMIN`, `SUPER_ADMIN`), `created_at`
- [ ] مطابق لجدول `ADMIN` في الـ ERD بالظبط

### `backend/accounts/serializers.py`

- [ ] `LoginSerializer`: `username`, `password`
- [ ] `RefreshSerializer`: `refreshToken`
- [ ] `AdminSerializer`: للعرض فقط (من غير password)

### `backend/accounts/views.py`

- [ ] `POST /auth/login` — يتحقق من username/password، يرجع `accessToken`, `refreshToken`, `expiresIn`, `role` (زي ما هو موثق بالظبط في API Contract بند 11)
- [ ] `POST /auth/refresh` — ياخد `refreshToken`، يرجع `accessToken` جديد + `expiresIn` (بند 12)
- [ ] Error handling: `401` لو بيانات غلط

### `backend/accounts/permissions.py`

- [ ] `IsAdmin`: يسمح لـ role `ADMIN` أو `SUPER_ADMIN`
- [ ] `IsSuperAdmin`: يسمح لـ `SUPER_ADMIN` بس (يُستخدم في `POST /atms` و`PATCH /atms/{atmId}` — هتتبع مع محمد على الـ RBAC matrix بند 19)

### `backend/accounts/urls.py`

- [ ] `path("auth/login/", ...)`, `path("auth/refresh/", ...)`

### `backend/accounts/tests/test_login.py`

- [ ] Test: login صح يرجع 200 + التوكنز
- [ ] Test: login غلط يرجع 401

### `backend/accounts/tests/test_permissions.py`

- [ ] Test: `IsSuperAdmin` بيرفض role=`ADMIN` على endpoint محمي
- [ ] Test: `IsSuperAdmin` بيسمح لـ role=`SUPER_ADMIN`

---

### `backend/common/exceptions.py`

- [ ] Custom exception handler لـ DRF يحول أي error لشكل موحد:
  ```json
  { "error": { "code": "...", "message": "...", "details": null } }
  ```
  (نفس الشكل الموثق في API Contract بند 4)

### `backend/common/pagination.py`

- [ ] Custom `PageNumberPagination` يرجع `{ "data": [...], "pagination": { "page", "limit", "total", "totalPages" } }` — نفس الشكل المستخدم في `GET /atms` و`GET /notifications`

### `backend/common/api_key_auth.py`

- [ ] DRF Authentication class تقرأ header `X-API-Key`، تتحقق منه (تقارنه بالـ hash المخزن لكل ATM أو مفتاح عام + IP whitelist)، تُستخدم في كل الـ ATM-facing endpoints (heartbeat, routing/alternatives, notifications/sms, transactions/attempt)

---

### 🆕 `kiosk/package.json` / `Dockerfile` / `.env.example`

- [ ] Dependencies: `react`, state management خفيف (`zustand` أو `useReducer` بسيط) — **من غير `react-router-dom`**، الفلو خطي بمرحلة (step) في الـ session state
- [ ] `Dockerfile`: multi-stage زي `frontend/` بالظبط (`node` build ثم `nginx`)
- [ ] `.env.example`: `VITE_API_BASE_URL`, `VITE_ATM_API_KEY` (مفتاح ثابت للماكينة، مش JWT), `VITE_ATM_ID`

### 🆕 `kiosk/src/store/sessionSlice.js`

- [ ] الحالة: `{ step, requestedService, requestedAmount, redirectReason, alternatives, chosenAtmId, phoneNumber }`
- [ ] `resetSession()`: بترجع كل حاجة لـ null — لازم تتنادى تلقائيًا بعد شاشة التأكيد (SCR-06) أو بعد timeout (مثلاً 60 ثانية من غير تفاعل)
- [ ] **ممنوع** أي persistence (لا localStorage ولا sessionStorage) — الحالة في الـ memory بس، لأن الماكينة جهاز مشترك

### 🆕 `kiosk/src/services/api.js`

- [ ] `attemptTransaction({ requestedService, requestedAmount })` → `POST /atms/{atmId}/transactions/attempt`
- [ ] `getAlternatives(...)` → `POST /routing/alternatives` (لو محتاجينها منفصلة عن attempt)
- [ ] `requestSms({ phoneNumber, chosenAtmId })` → `POST /notifications/sms`
- [ ] كل نداء يحط `X-API-Key: VITE_ATM_API_KEY` — **مفيش JWT هنا خالص**، الكشك مش بيعمل login

### 🆕 `kiosk/src/pages/SelectService.jsx` (SCR-01)

- [ ] شبكة أزرار الخدمات (WITHDRAWAL/DEPOSIT/CURRENCY_EXCHANGE/CHECK_DEPOSIT) + لوحة إدخال مبلغ لو الخدمة WITHDRAWAL
- [ ] زرار "متابعة" بينده `api.attemptTransaction({ requestedService, requestedAmount })` وينقل الـ session لـ step التالية

### 🆕 `kiosk/src/components/ServiceGrid.jsx` + `AmountPad.jsx`

- [ ] `ServiceGrid.jsx`: أزرار الخدمات الأربعة، الزرار المختار عليه حالة `active`
- [ ] `AmountPad.jsx`: عرض المبلغ بخط كبير + إدخاله (رقمي فقط)

---

## 👤 محمد — `atms/` (ATM Management) + `kiosk/` SCR-05, SCR-06

### `backend/atms/models.py`

- [ ] Model `ATM`: مطابق تمامًا لجدول ATM في الـ ERD المُحدّث:
      `atm_id` (PK), `branch_name`, `latitude`, `longitude`, `status` (ONLINE/OFFLINE/MAINTENANCE), `cash_status` (AVAILABLE/LOW/EMPTY), **`current_cash_balance` (float)**, `last_heartbeat_at`, `created_at`, `updated_at`
- [ ] Model `Service`: `service_id` (PK), `name`
- [ ] Model `ATM_Service` (many-to-many through table): `atm_id` FK, `service_id` FK
- [ ] Model `HeartbeatLog`: `heartbeat_id` (PK), `atm_id` FK, `status`, `cash_status`, `received_at`
- [ ] Method `hasSufficientCash(requestedAmount, buffer)` على الـ model نفسه (بترجع bool) — هتُستخدم من سارة في الـ Routing Engine

### `backend/atms/serializers.py`

- [ ] `ATMListSerializer`: للاستخدام في `GET /atms` (نفس حقول بند 13 في الـ Contract)
- [ ] `ATMDetailSerializer`: زي فوق + `recentHeartbeats[]` (بند 14)
- [ ] `HeartbeatSerializer`: `status`, `cashStatus`, `cashBalance`, `services`, `latitude`, `longitude`, `timestamp` (بند 6)
- [ ] `ATMCreateSerializer` / `ATMUpdateSerializer` (بند 15، 16)

### `backend/atms/views.py`

- [ ] `POST /atms/{atmId}/heartbeat` — auth: `X-API-Key`، يحدث `status`, `cash_status`, `current_cash_balance` من `cashBalance`، يسجل `HeartbeatLog`، يبعت الحدث على WebSocket (عن طريق `consumers.py`) خلال أقل من 2 ثانية
- [ ] `POST /atms/{atmId}/transactions/attempt` — auth: `X-API-Key`، ياخد `requestedService` و`requestedAmount` (لو WITHDRAWAL)، يفحص حالة الماكينة والرصيد، يرجع `PROCEED` أو `REDIRECT` (لو REDIRECT ينادي `RoutingEngine.findAlternatives` من app `routing` بتاع سارة)
- [ ] `GET /atms` — auth: JWT (ADMIN/SUPER_ADMIN)، فلاتر: `status`, `cashStatus`, `service`, `lat/lng/radiusKm`, pagination (بند 13)
- [ ] `GET /atms/{atmId}` — auth: JWT، تفاصيل + `recentHeartbeats[]` (بند 14)
- [ ] `POST /atms` — auth: JWT + `IsSuperAdmin`، تسجيل ماكينة جديدة (بند 15)
- [ ] `PATCH /atms/{atmId}` — auth: JWT + `IsSuperAdmin`، تعديل جزئي (بند 16)
- [ ] `GET /services` — يرجع كل الـ Service types (بند 17)
- [ ] 🆕 `GET /atms/network-stats` — auth: JWT، يرجع `{ onlineCount, lowCashCount, offlineCount, uptimePercentage }` — بيغذي الـ KPI row في أعلى شاشة SCR-A2 (Live Dashboard). `uptimePercentage` تقدر تحسبه من نسبة الوقت اللي الماكينة كانت `ONLINE` فيه خلال آخر 30 يوم من `HeartbeatLog`

### `backend/atms/consumers.py`

- [ ] `DashboardConsumer` (Django Channels): يتحقق من JWT جاي في query param `?token=`
- [ ] عند أي تحديث heartbeat، يبعت event `atm.status.updated` بالـ payload الموثق في بند 18
- [ ] لو تغيير الحالة يحتاج انتباه (مثلاً بقت OFFLINE)، يبعت كمان `atm.alert`

### `backend/atms/urls.py`

- [ ] اربط كل الـ endpoints فوق بمساراتها

### `backend/atms/tests/test_heartbeat.py`

- [ ] Test: heartbeat صحيح يحدّث `current_cash_balance` صح
- [ ] Test: heartbeat من غير API key صحيح يرجع 401
- [ ] Test: heartbeat لـ atmId مش موجود يرجع 404

### `backend/atms/tests/test_transaction_attempt.py`

- [ ] Test: ATM شغالة وفيها كاش كافي → `outcome: PROCEED`
- [ ] Test: ATM offline → `outcome: REDIRECT`, `reason: OFFLINE`
- [ ] Test: ATM شغالة بس الكاش أقل من `requestedAmount + buffer` → `outcome: REDIRECT`, `reason: INSUFFICIENT_CASH`

### `backend/atms/tests/test_websocket.py`

- [ ] Test: الاتصال بالـ WebSocket من غير token يترفض
- [ ] Test: heartbeat بيولّد event `atm.status.updated` بالشكل الصح

### 🆕 `backend/atms/tests/test_network_stats.py`

- [ ] Test: العدّادات (`onlineCount`/`lowCashCount`/`offlineCount`) بتطابق عدد الماكينات الفعلي حسب حالتها
- [ ] Test: `uptimePercentage` بيرجع رقم منطقي (بين 0 و100) حتى لو الماكينة جديدة ومفيهاش تاريخ heartbeat كافي

---

### 🆕 `kiosk/src/pages/PhoneNumberEntry.jsx` (SCR-05)

- [ ] حقل إدخال رقم موبايل + رابط "تخطي وطباعة الاتجاهات فقط"
- [ ] زرار "إرسال" بينده `api.requestSms({ phoneNumber, chosenAtmId })`
- [ ] بعد الإرسال: امسح `phoneNumber` من الـ session state فورًا (متسيبهاش قاعدة لحد ما تتعمل reset — نفس مبدأ NFR الخاص بعدم تخزين الرقم)

### 🆕 `kiosk/src/pages/Confirmation.jsx` (SCR-06)

- [ ] رسالة نجاح + زرار "إنهاء" بينده `resetSession()` (من `sessionSlice.js` بتاع عبدالله) ويرجع لـ `SelectService`

### 🆕 `kiosk/src/components/PhoneInput.jsx` + `SuccessCheck.jsx`

- [ ] `PhoneInput.jsx`: حقل رقم موبايل، تنسيق مصري (`01xx xxx xxxx`)
- [ ] `SuccessCheck.jsx`: أنيميشن علامة صح بسيطة

### 🆕 `kiosk/src/__tests__/pages/PhoneNumberEntry.test.jsx`

- [ ] Test: الـ state بيتمسح فورًا بعد الإرسال (regression test يوازي `test_no_phone_persistence.py` بتاع الباك إند بالظبط)

---

## 👤 سارة — `routing/` + `notifications/`

### `backend/routing/services.py`

- [ ] Class `RoutingEngine`:
  - `find_alternatives(origin_atm_id, lat, lng, requested_service, requested_amount=None, radius_km=5)`:
    1. فلتر الماكينات: `status=ONLINE`, بتدعم `requested_service`, جوه الـ `radius_km`
    2. لو `requested_amount` موجود (يعني WITHDRAWAL): استبعد أي ماكينة `current_cash_balance < requested_amount + buffer_amount`
    3. نادِ `MappingGateway.get_distance_matrix()` لحساب المسافة والـ ETA
    4. رجّع أعلى 3 مرتبين بالمسافة
  - `fallback_haversine(origin, candidates)`: يتنفذ تلقائيًا لو `MappingGateway` رمى exception (Timeout/فشل الـ API)
  - `buffer_amount`: قيمة ثابتة في الإعدادات (settings) أو نسبة من `requested_amount` — **متبعتش قيمتها للـ client أبدًا**

### `backend/routing/gateways.py`

- [ ] Class `MappingGateway`:
  - `get_distance_matrix(origin, destinations)`: نداء لـ Google Maps Distance Matrix API، يرجع `distanceKm` و`etaMinutes` لكل destination
  - `get_eta(origin, destination)`: نداء مفرد
  - Timeout قصير (مثلاً 2 ثانية) عشان الـ NFR بتاع الـ 3 ثواني ميتأثرش

### `backend/routing/views.py`

- [ ] `POST /routing/alternatives` — auth: `X-API-Key`، بينادي `RoutingEngine.find_alternatives()`، يرجع الشكل الموثق في بند 7 (فيه `distanceSource` يوضح `GOOGLE_MAPS` أو `HAVERSINE_FALLBACK`، وفيه `availableCashBalance` لو كان في `requestedAmount`)
- [ ] Error handling: `404` لو مفيش نتائج، `503` لو الـ routing engine مش متاح

### `backend/routing/urls.py`

- [ ] اربط `POST /routing/alternatives`

### `backend/routing/tests/test_routing_engine.py`

- [ ] Test: الفلترة بالـ radius شغالة صح
- [ ] Test: الفلترة بالـ cash-sufficiency (`current_cash_balance >= requestedAmount + buffer`) شغالة صح
- [ ] Test: النتيجة بترجع أعلى 3 بس مرتبة بالمسافة

### `backend/routing/tests/test_haversine_fallback.py`

- [ ] Test: لو `MappingGateway` رمى exception، الـ Engine يستخدم `fallback_haversine` تلقائيًا و`distanceSource` بيبقى `HAVERSINE_FALLBACK`

---

### `backend/notifications/models.py`

- [ ] Model `Notification`: `notification_id` (PK), `atm_id` FK, `message`, `status` (QUEUED/SENT/DELIVERED/FAILED), `sent_at`
- [ ] 🆕 حقل `requested_service` (نفس الـ choices بتاعة `ATM.services`) — عشان جدول الإشعارات في شاشة SCR-A3 يعرض عمود "الخدمة المؤكدة" من بيانات حقيقية، مش parsing من نص الرسالة
- [ ] **مهم:** مفيش حقل لرقم الموبايل خالص في الـ model — ده الـ NFR بتاع الـ Data Minimization

### `backend/notifications/tasks.py`

- [ ] Celery task `dispatch_sms(phone_number, chosen_atm_id, requested_service)`:
  1. يبني الرسالة (عنوان الماكينة + تأكيد الخدمة + رابط Google Maps)
  2. يبعتها عن طريق Twilio
  3. يسجل `Notification` (من غير رقم الموبايل، مع 🆕 `requested_service`)
  4. يمسح `phone_number` من الـ memory بعد التنفيذ (متتخزنش في أي مكان)

### `backend/notifications/views.py`

- [ ] `POST /notifications/sms` — auth: `X-API-Key`، يستقبل `phoneNumber`, `chosenAtmId`, `requestedService`، ينده `dispatch_sms.delay(...)`، يرجع `202` مع `taskId` (بند 8)
- [ ] `GET /notifications/sms/{taskId}/status` — auth: `X-API-Key`، بولينج لحالة الـ Celery task (بند 9)
- [ ] `GET /notifications` — auth: JWT (ADMIN/SUPER_ADMIN)، list/filter بـ `atmId`, `status`, `dateFrom`, `dateTo` + pagination (بند 10)، 🆕 حط `requestedService` في الـ response — **الـ response ميرجعش رقم الموبايل خالص**

### `backend/notifications/urls.py`

- [ ] اربط الـ 3 endpoints فوق

### `backend/notifications/tests/test_sms_dispatch.py`

- [ ] Test: `POST /notifications/sms` برقم صحيح يرجع `202` + `taskId`
- [ ] Test: رقم موبايل غلط الشكل يرجع `400`

### `backend/notifications/tests/test_no_phone_persistence.py`

- [ ] Test صريح: بعد تنفيذ `dispatch_sms`، الـ `Notification` المخزن في الداتابيز **ميحتويش** على رقم الموبايل في أي حقل (regression test دايم يفضل شغال مع أي تعديل مستقبلي)

---

## 👤 صفية — `frontend/` (Admin Dashboard) + `kiosk/` SCR-02, SCR-03, SCR-04

> ملحوظة: تصميم الـ Admin Dashboard (الألوان، الخطوط) جاهز في ملف `sars-dashboard-ui.jsx` اللي عملناه قبل كده — دورك تفصله لملفات منظمة زي البنية تحت، وتوصله بالـ API الحقيقي بدل الـ mock data. تصميم شاشات الـ Kiosk جاي من ملف `sars_UI-UX.html` اللي بعته (نفس الـ HTML/CSS بتاعه ينفع أساس لمكونات الـ React). شاشات SCR-02/03/04 بتعتمد على `sessionSlice.js` و`services/api.js` اللي عبدالله هيجهزهم في `kiosk/` — لازم يخلصهم الأول.

### `frontend/package.json`

- [ ] Dependencies: `react`, `react-router-dom`, `axios` (أو `fetch` wrapper)، state management (`zustand` أو `redux-toolkit`)، `lucide-react`، Tailwind

### `frontend/Dockerfile`

- [ ] Multi-stage build: `node` للـ build، `nginx` لتقديم الملفات الناتجة

### `frontend/.env.example`

- [ ] `VITE_API_BASE_URL=http://localhost:8000/api/v1`
- [ ] `VITE_WS_URL=ws://localhost:8000/ws/dashboard`

### `frontend/src/services/api.js`

- [ ] `login(username, password)` → `POST /auth/login`
- [ ] `refreshToken(refreshToken)` → `POST /auth/refresh`
- [ ] `getATMs(filters)` → `GET /atms`
- [ ] `getATMDetail(atmId)` → `GET /atms/{atmId}`
- [ ] `createATM(payload)` / `updateATM(atmId, payload)` (لـ SUPER_ADMIN فقط)
- [ ] `getServices()` → `GET /services`
- [ ] `getNotifications(filters)` → `GET /notifications`
- [ ] كل نداء يحط `Authorization: Bearer <token>` تلقائيًا من الـ authSlice

### `frontend/src/services/socket.js`

- [ ] يفتح اتصال WebSocket على `VITE_WS_URL?token=<accessToken>`
- [ ] `onMessage`: يميز بين `atm.status.updated` و`atm.alert` ويحدث الـ store (`atmsSlice`)
- [ ] Reconnect logic لو الاتصال اتقطع

### `frontend/src/store/atmsSlice.js`

- [ ] الحالة: `{ atms: [], selectedATM: null, filters: {...} }`
- [ ] Actions: `setATMs`, `updateATMStatus` (بتتنادى من `socket.js` عند أي `atm.status.updated`), `selectATM`, `setFilters`

### `frontend/src/store/authSlice.js`

- [ ] الحالة: `{ accessToken, refreshToken, role, isAuthenticated }`
- [ ] Actions: `login`, `logout`, `refreshAccessToken`
- [ ] يخزن التوكنز بأمان (مش localStorage للـ refresh token لو ممكن — فكروا سوا في الطريقة الأنسب)

### `frontend/src/pages/Login.jsx`

- [ ] فورم username/password، بينادي `api.login()`، لو نجح يحفظ التوكنز في `authSlice` ويوجه لـ `LiveMap`
- [ ] التصميم جاهز في `sars-dashboard-ui.jsx` (component `LoginPage`)

### `frontend/src/pages/LiveMap.jsx`

- [ ] عند التحميل: `api.getATMs()` يملأ `atmsSlice`، ويفتح اتصال `socket.js`
- [ ] فلاتر الحالة والبحث (موجودين في التصميم الجاهز)
- [ ] عند اختيار ATM: ينادي `api.getATMDetail(atmId)` عشان يجيب `recentHeartbeats[]` كمان

### `frontend/src/pages/Notifications.jsx`

- [ ] عند التحميل: `api.getNotifications()` مع الفلاتر
- [ ] Pagination لو النتايج كتير

### `frontend/src/components/`

- [ ] فصل الأجزاء المشتركة من `sars-dashboard-ui.jsx` لملفات منفصلة: `Sidebar.jsx`, `ATMRow.jsx`, `NetworkMap.jsx`, `ReceiptPanel.jsx`, `StatusBadge.jsx`, `Legend.jsx`

### `frontend/src/utils/`

- [ ] `formatCurrency.js`: تنسيق `current_cash_balance` بصيغة EGP
- [ ] `formatDate.js`: تنسيق `ISO8601` لصيغة قابلة للقراءة (زي "2 min ago")
- [ ] `statusMeta.js`: نقل الـ `STATUS_META`/`NOTIF_META` objects من التصميم الجاهز لملف مشترك

### `frontend/src/__tests__/`

- [ ] `components/ATMRow.test.jsx`: يتأكد إن اللون بيتغير حسب الـ status/cashStatus صح
- [ ] `services/api.test.js`: mock للـ fetch/axios، يتأكد إن الـ headers بتتبعت صح (Authorization, X-API-Key)

---

### 🆕 `kiosk/src/pages/CheckingStatus.jsx` (SCR-02)

- [ ] شاشة تحميل بس (spinner/radar) — تفضل معروضة لحد ما رد الـ `transactions/attempt` يرجع
- [ ] لازم يكون عندها حد أقصى انتظار (مثلاً 3.5 ثانية) وبعدها تعرض رسالة خطأ لو الـ backend اتأخر — عشان NFR الـ 3 ثواني

### 🆕 `kiosk/src/pages/Unavailable.jsx` (SCR-03)

- [ ] تتفعّل لو `outcome === "REDIRECT"`
- [ ] النص والأيقونة بيتغيروا حسب `reason` (`OFFLINE`/`MAINTENANCE`/`NO_CASH`/`INSUFFICIENT_CASH`) — استخدم mapping object زي `STATUS_META` في التصميم
- [ ] زرار "عرض الماكينات البديلة" → يودي لـ `AlternativesList`

### 🆕 `kiosk/src/pages/AlternativesList.jsx` (SCR-04)

- [ ] يعرض الـ `alternatives[]` الجاية من `transactions/attempt` (أو من نداء منفصل لـ `routing/alternatives` لو الـ backend فصلهم)
- [ ] كل كارت: اسم الفرع، المسافة، الـ ETA، badge "متاح" (من `availableCashBalance` الموجود في الـ response — **من غير ما تعرض الرقم نفسه**)
- [ ] اختيار كارت يحفظ `chosenAtmId` في الـ session

### 🆕 `kiosk/src/components/StatusRadar.jsx` + `AlternativeCard.jsx`

- [ ] `StatusRadar.jsx`: أنيميشن الـ radar/spinner المستخدم في SCR-02
- [ ] `AlternativeCard.jsx`: كارت الفرع البديل (اسم، مسافة، ETA، badge)

### 🆕 `kiosk/src/__tests__/pages/Unavailable.test.jsx`

- [ ] Test: كل قيمة من الـ 4 بتوع `reason` بتغيّر النص/الأيقونة الصح
