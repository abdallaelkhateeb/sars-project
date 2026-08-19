# Smart ATM Routing System (SARS) — Final Project Structure (v2)

Covers all FRs/NFRs, the Class/ERD/C4/Sequence diagrams, the API Contract, and the 9-screen UI/UX proposal (customer kiosk + admin dashboard). New/changed items vs. the previous version are marked 🆕.

```
sars-project/
├── .git/
├── .gitignore                    # venv, node_modules, .env, __pycache__, media/
├── .env.example                  # 🆕 template for root-level shared vars (if any)
├── README.md                     # project overview + setup steps for the team
├── docker-compose.yml            # runs backend + frontend + db + redis together
│
├── docs/                         # 🆕 keeps diagrams & contract versioned with the code
│   ├── diagrams/
│   │   ├── class-diagram.md
│   │   ├── erd.md
│   │   ├── c4-container-diagram.md
│   │   └── sequence-diagram.md
│   └── api-contract.md
│
├── .github/                      # 🆕 CI/CD (NFR 5)
│   └── workflows/
│       ├── backend-ci.yml        # lint + pytest on push/PR
│       └── frontend-ci.yml       # lint + jest/vitest on push/PR
│
├── backend/                      # Django
│   ├── manage.py
│   ├── requirements.txt
│   ├── requirements-dev.txt      # 🆕 pytest, flake8/ruff, coverage
│   ├── Dockerfile
│   ├── .env.example              # 🆕 DB_URL, REDIS_URL, GOOGLE_MAPS_API_KEY,
│   │                              #     TWILIO_SID/TOKEN, JWT_SECRET, ATM_API_KEY_SALT
│   ├── pytest.ini                # 🆕
│   │
│   ├── sars_core/                # project settings (settings, urls, asgi/wsgi)
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   └── prod.py
│   │   ├── celery.py             # Celery config (Task Queue container)
│   │   └── asgi.py               # WebSocket entrypoint (Django Channels)
│   │
│   ├── accounts/                 # 🆕 Admin auth & RBAC (NFR 4)
│   │   ├── models.py             # Admin model (username, role: ADMIN/SUPER_ADMIN)
│   │   ├── serializers.py
│   │   ├── views.py              # /auth/login, /auth/refresh
│   │   ├── permissions.py        # IsAdmin, IsSuperAdmin (RBAC)
│   │   ├── urls.py
│   │   └── tests/                # 🆕
│   │       ├── test_login.py
│   │       └── test_permissions.py
│   │
│   ├── atms/                     # ATM management (Class: ATM, ServiceType)
│   │   ├── models.py             # ATM (incl. current_cash_balance), Service, ATM_Service
│   │   ├── serializers.py
│   │   ├── views.py              # /atms, /atms/{id}, /atms/{id}/heartbeat,
│   │   │                          #   /atms/{id}/transactions/attempt,
│   │   │                          #   🆕 /atms/network-stats (online/low-cash/offline
│   │   │                          #   counts + uptime %, backs the admin KPI row)
│   │   ├── consumers.py          # WebSocket consumer -> /ws/dashboard
│   │   ├── urls.py
│   │   └── tests/                # 🆕
│   │       ├── test_heartbeat.py
│   │       ├── test_transaction_attempt.py
│   │       └── test_websocket.py
│   │
│   ├── routing/                  # Routing Engine
│   │   ├── services.py           # 🆕 RoutingEngine class: findAlternatives(),
│   │   │                          #   filterByRadius(), cash-sufficiency filter,
│   │   │                          #   fallbackHaversine()
│   │   ├── gateways.py           # 🆕 MappingGateway wrapper (Google Maps client)
│   │   ├── views.py              # /routing/alternatives
│   │   ├── urls.py
│   │   └── tests/                # 🆕
│   │       ├── test_routing_engine.py     # incl. cash-sufficiency + buffer logic
│   │       └── test_haversine_fallback.py # mapping API failure path
│   │
│   ├── notifications/             # SMS notifications
│   │   ├── models.py             # Notification (no phone number persisted)
│   │   │                          # 🆕 requestedService field added — so the admin
│   │   │                          #   "Notifications" table can show a real confirmed-
│   │   │                          #   service column instead of parsing free text
│   │   ├── tasks.py              # Celery task: SMSService.sendSMS / dispatchAsync
│   │   ├── views.py              # /notifications/sms, /notifications/sms/{id}/status,
│   │   │                          #   /notifications (admin list)
│   │   ├── urls.py
│   │   └── tests/                # 🆕
│   │       ├── test_sms_dispatch.py
│   │       └── test_no_phone_persistence.py  # explicit NFR 4 regression test
│   │
│   └── common/                   # 🆕 shared utilities across apps
│       ├── exceptions.py         # standard error object format
│       ├── pagination.py
│       └── api_key_auth.py       # X-API-Key auth class for ATM endpoints
│
├── frontend/                     # React (Admin Dashboard — internal, bank staff only)
│   ├── package.json
│   ├── Dockerfile
│   ├── .env.example               # 🆕 VITE_API_BASE_URL, VITE_WS_URL
│   ├── public/
│   └── src/
│       ├── assets/                # images, icons, marker colors
│       ├── components/            # buttons, inputs, ATM marker, status badge
│       ├── pages/                 # Login (SCR-A1), LiveMap (SCR-A2),
│       │                          #   Notifications (SCR-A3, incl. ATM detail slide-over)
│       ├── services/              # api.js (REST calls), socket.js (WebSocket client)
│       ├── store/                 # 🆕 real-time ATM state (Redux/Zustand/Context)
│       │   ├── atmsSlice.js       # holds live status pushed via WebSocket
│       │   └── authSlice.js       # JWT/session state
│       ├── utils/                 # date/distance formatting
│       └── __tests__/             # 🆕
│           ├── components/
│           └── services/
│
└── kiosk/                        # 🆕 React (ATM Interface — embedded kiosk app, customer-facing)
    │                              #   Matches the "ATM Interface" container in the C4 diagram —
    │                              #   was already planned there but had no home until now.
    ├── package.json
    ├── Dockerfile
    ├── .env.example               # 🆕 VITE_API_BASE_URL, VITE_ATM_API_KEY, VITE_ATM_ID
    ├── public/
    └── src/
        ├── assets/                # SARS branding, service icons
        ├── components/            # ServiceGrid, AmountPad, StatusRadar, AlternativeCard,
        │                          #   PhoneInput, SuccessCheck
        ├── pages/                 # 🆕 one file per kiosk screen:
        │   ├── SelectService.jsx        # SCR-01 — service + requestedAmount
        │   ├── CheckingStatus.jsx       # SCR-02 — loading/spinner, <3s budget
        │   ├── Unavailable.jsx          # SCR-03 — reason: OFFLINE/MAINTENANCE/
        │   │                            #   NO_CASH/INSUFFICIENT_CASH
        │   ├── AlternativesList.jsx     # SCR-04 — top 3, no real balance shown
        │   ├── PhoneNumberEntry.jsx     # SCR-05 — phone input, "skip" option
        │   └── Confirmation.jsx         # SCR-06 — success state
        ├── services/
        │   └── api.js             # attemptTransaction(), getAlternatives(),
        │                          #   requestSms() — all via X-API-Key, no JWT
        ├── store/                 # 🆕 local session state only (no persistence —
        │                          #   resets every transaction; phone number never
        │                          #   written to any store/localStorage)
        │   └── sessionSlice.js
        ├── utils/
        └── __tests__/             # 🆕
            └── pages/
```

---

## What each 🆕 addition closes

| Gap (from the review)                           | Addition                                                                            |
| ----------------------------------------------- | ----------------------------------------------------------------------------------- |
| No dedicated Admin auth/RBAC module             | `backend/accounts/` (models, permissions, views for `/auth/login`, `/auth/refresh`) |
| No test structure                               | `tests/` inside every backend app + `frontend/src/__tests__/`                       |
| No CI/CD config                                 | `.github/workflows/backend-ci.yml`, `frontend-ci.yml`                               |
| No secrets/env management                       | `.env.example` in root, `backend/`, and `frontend/`                                 |
| Routing logic not isolated from views           | `routing/services.py` (RoutingEngine) + `routing/gateways.py` (MappingGateway)      |
| No real-time state layer on the frontend        | `frontend/src/store/atmsSlice.js`                                                   |
| Diagrams/contract not versioned with code       | `docs/diagrams/` + `docs/api-contract.md`                                           |
| 🆕 6 kiosk screens (customer flow) had no home  | New top-level `kiosk/` app, separate from `frontend/`                               |
| 🆕 "Uptime this month" KPI had no data source   | New `GET /atms/network-stats` endpoint                                              |
| 🆕 "Confirmed service" column had no real field | `Notification.requestedService` field added                                         |

## Notes

- `notifications/tests/test_no_phone_persistence.py` is called out on purpose — it's the automated check that guards the NFR 4 "Data Minimization" requirement over time, not just a code comment.
- `routing/services.py` is where the cash-sufficiency filter (`current_cash_balance >= requestedAmount + buffer_amount`) and the Haversine fallback both live, isolated from `views.py` so they're unit-testable without spinning up the API.
- `sars_core/settings/` is split into `base/dev/prod` instead of a single `settings.py` — makes the Dockerfile and CI config point at `prod.py` while local dev uses `dev.py`, without duplicating shared settings.
- `kiosk/` is a **separate app from `frontend/`** on purpose — it matches the distinct "ATM Interface" container in the C4 diagram, has different auth (`X-API-Key`, no JWT/login), and must never store the customer's phone number anywhere, including local component state beyond the single request.
- `kiosk/src/store/sessionSlice.js` is intentionally _not_ persisted (no localStorage) — every screen's state should reset when a transaction ends or times out, since this runs on a shared physical machine.
