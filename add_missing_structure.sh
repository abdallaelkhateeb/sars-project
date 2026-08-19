#!/usr/bin/env bash
# ============================================================================
# SARS — add_missing_structure.sh
#
# Adds whatever is MISSING from the final v2 project structure
# (docs/, .github/workflows/, accounts/, common/, kiosk/, tests/, store/, ...)
# to an EXISTING sars-project repo, without touching anything already there.
#
# Usage:
#   1. Copy this file into the root of your cloned sars-project repo
#      (the folder that contains backend/ and frontend/).
#   2. Run:  bash add_missing_structure.sh
#   3. Review with `git status`, then commit.
#
# Safe to run more than once — every file/folder is only created if it
# does not already exist. Nothing is ever overwritten or deleted.
# ============================================================================
 
set -euo pipefail
 
CREATED=0
SKIPPED=0
 
# ---- helpers --------------------------------------------------------------
 
ensure_dir() {
  local dir="$1"
  if [ ! -d "$dir" ]; then
    mkdir -p "$dir"
    echo "  [dir]  created  $dir"
  fi
}
 
# comment_for_ext EXT -> prints the right line-comment prefix
comment_for_ext() {
  case "$1" in
    py)   echo "#" ;;
    js|jsx) echo "//" ;;
    md)   echo "#" ;;
    yml|yaml) echo "#" ;;
    ini)  echo "#" ;;
    *)    echo "#" ;;
  esac
}
 
# ensure_file PATH "TODO text"
# Creates the file with a single TODO comment line if it does not exist yet.
# Skips silently (counted) if the file is already there.
ensure_file() {
  local path="$1"
  local todo="$2"
  local dir
  dir="$(dirname "$path")"
  ensure_dir "$dir"
 
  if [ -f "$path" ]; then
    SKIPPED=$((SKIPPED + 1))
    return
  fi
 
  local ext="${path##*.}"
  local c
  c="$(comment_for_ext "$ext")"
 
  {
    echo "$c TODO: $todo"
    echo "$c See SARS-Task-Breakdown.md for the full checklist for this file."
  } > "$path"
 
  CREATED=$((CREATED + 1))
  echo "  [file] created  $path"
}
 
# ensure_empty_dir_marker DIR -> keeps an otherwise-empty folder in git
ensure_empty_dir_marker() {
  local dir="$1"
  ensure_dir "$dir"
  if [ -z "$(ls -A "$dir" 2>/dev/null)" ]; then
    touch "$dir/.gitkeep"
    CREATED=$((CREATED + 1))
    echo "  [file] created  $dir/.gitkeep"
  fi
}
 
echo "== SARS — adding missing project structure =="
echo
 
# ---- root ------------------------------------------------------------------
echo "-- root --"
ensure_file ".gitignore" "venv/, __pycache__/, node_modules/, .env, dist/, build/, *.sqlite3, media/"
ensure_file "README.md" "project overview + setup steps for the team"
ensure_file "docker-compose.yml" "db (postgis), redis, backend, celery, frontend, kiosk services"
ensure_file ".env.example" "root-level shared vars, or a pointer to backend/.env.example and frontend/.env.example"
 
# ---- docs (new) --------------------------------------------------------------
echo "-- docs/ --"
ensure_file "docs/diagrams/class-diagram.md" "paste the Class Diagram mermaid source here"
ensure_file "docs/diagrams/erd.md" "paste the ERD mermaid source here (incl. current_cash_balance)"
ensure_file "docs/diagrams/c4-container-diagram.md" "paste the C4 Container Diagram mermaid source here"
ensure_file "docs/diagrams/sequence-diagram.md" "paste the Sequence Diagram mermaid source here"
ensure_file "docs/api-contract.md" "paste the full API Contract (table format) here"
 
# ---- CI/CD (new) --------------------------------------------------------------
echo "-- .github/workflows/ --"
ensure_file ".github/workflows/backend-ci.yml" "lint (flake8/ruff) + pytest on push/PR touching backend/**"
ensure_file ".github/workflows/frontend-ci.yml" "lint + test on push/PR touching frontend/** and kiosk/**"
 
# ---- backend/sars_core -------------------------------------------------------
echo "-- backend/sars_core/ --"
ensure_file "backend/manage.py" "standard Django manage.py entrypoint"
ensure_file "backend/requirements.txt" "django, djangorestframework, channels, channels-redis, celery, redis, psycopg2-binary, djangorestframework-simplejwt, requests"
ensure_file "backend/requirements-dev.txt" "pytest, pytest-django, pytest-cov, flake8 or ruff"
ensure_file "backend/Dockerfile" "python:3.12-slim base, pip install, CMD runs daphne (ASGI, needed for WebSocket)"
ensure_file "backend/.env.example" "DB_*, REDIS_URL, JWT_SECRET, GOOGLE_MAPS_API_KEY, TWILIO_*, ATM_API_KEY_SALT"
ensure_file "backend/pytest.ini" "DJANGO_SETTINGS_MODULE = sars_core.settings.dev"
ensure_file "backend/sars_core/__init__.py" "empty — marks sars_core as a package"
ensure_file "backend/sars_core/settings/__init__.py" "empty — marks settings as a package"
ensure_file "backend/sars_core/settings/base.py" "INSTALLED_APPS, DATABASES, REST_FRAMEWORK, CHANNEL_LAYERS, CELERY_* — see task breakdown"
ensure_file "backend/sars_core/settings/dev.py" "DEBUG=True, ALLOWED_HOSTS=['*'], imports from base.py"
ensure_file "backend/sars_core/settings/prod.py" "DEBUG=False, ALLOWED_HOSTS from env, extra security settings"
ensure_file "backend/sars_core/celery.py" "standard Celery app setup, autodiscover_tasks()"
ensure_file "backend/sars_core/asgi.py" "ProtocolTypeRouter: http + websocket (atms/consumers.py)"
 
# ---- backend/accounts (new) --------------------------------------------------
echo "-- backend/accounts/ --"
ensure_file "backend/accounts/__init__.py" "empty — marks accounts as a package"
ensure_file "backend/accounts/models.py" "Admin model: admin_id, username, password_hash, role (ADMIN/SUPER_ADMIN), created_at"
ensure_file "backend/accounts/serializers.py" "LoginSerializer, RefreshSerializer, AdminSerializer"
ensure_file "backend/accounts/views.py" "POST /auth/login, POST /auth/refresh"
ensure_file "backend/accounts/permissions.py" "IsAdmin, IsSuperAdmin"
ensure_file "backend/accounts/urls.py" "wire up /auth/login and /auth/refresh"
ensure_file "backend/accounts/tests/__init__.py" "empty — marks tests as a package"
ensure_file "backend/accounts/tests/test_login.py" "valid login -> 200 + tokens; invalid -> 401"
ensure_file "backend/accounts/tests/test_permissions.py" "IsSuperAdmin rejects ADMIN, allows SUPER_ADMIN"
 
# ---- backend/atms -------------------------------------------------------------
echo "-- backend/atms/ --"
ensure_file "backend/atms/__init__.py" "empty — marks atms as a package"
ensure_file "backend/atms/models.py" "ATM (incl. current_cash_balance), Service, ATM_Service, HeartbeatLog, hasSufficientCash()"
ensure_file "backend/atms/serializers.py" "ATMListSerializer, ATMDetailSerializer, HeartbeatSerializer, ATMCreate/UpdateSerializer"
ensure_file "backend/atms/views.py" "heartbeat, transactions/attempt, /atms CRUD, /services, /atms/network-stats"
ensure_file "backend/atms/consumers.py" "DashboardConsumer — atm.status.updated / atm.alert over WebSocket"
ensure_file "backend/atms/urls.py" "wire up all atms/ endpoints"
ensure_file "backend/atms/tests/__init__.py" "empty — marks tests as a package"
ensure_file "backend/atms/tests/test_heartbeat.py" "valid heartbeat updates current_cash_balance; auth/404 errors"
ensure_file "backend/atms/tests/test_transaction_attempt.py" "PROCEED vs REDIRECT (OFFLINE/INSUFFICIENT_CASH/...)"
ensure_file "backend/atms/tests/test_websocket.py" "no-token connection rejected; heartbeat triggers atm.status.updated"
ensure_file "backend/atms/tests/test_network_stats.py" "counts match actual ATM statuses; uptimePercentage is sane"
 
# ---- backend/routing -----------------------------------------------------------
echo "-- backend/routing/ --"
ensure_file "backend/routing/__init__.py" "empty — marks routing as a package"
ensure_file "backend/routing/services.py" "RoutingEngine: find_alternatives(), cash-sufficiency filter, fallback_haversine()"
ensure_file "backend/routing/gateways.py" "MappingGateway: get_distance_matrix(), get_eta() (Google Maps client)"
ensure_file "backend/routing/views.py" "POST /routing/alternatives"
ensure_file "backend/routing/urls.py" "wire up /routing/alternatives"
ensure_file "backend/routing/tests/__init__.py" "empty — marks tests as a package"
ensure_file "backend/routing/tests/test_routing_engine.py" "radius filter, cash-sufficiency filter, top-3 sorted by distance"
ensure_file "backend/routing/tests/test_haversine_fallback.py" "mapping API failure -> distanceSource = HAVERSINE_FALLBACK"
 
# ---- backend/notifications -------------------------------------------------------
echo "-- backend/notifications/ --"
ensure_file "backend/notifications/__init__.py" "empty — marks notifications as a package"
ensure_file "backend/notifications/models.py" "Notification: notification_id, atm_id, message, requested_service, status, sent_at (NO phone field)"
ensure_file "backend/notifications/tasks.py" "Celery task dispatch_sms(): build message, send via Twilio, log Notification"
ensure_file "backend/notifications/views.py" "POST /notifications/sms, GET /notifications/sms/{taskId}/status, GET /notifications"
ensure_file "backend/notifications/urls.py" "wire up all notifications/ endpoints"
ensure_file "backend/notifications/tests/__init__.py" "empty — marks tests as a package"
ensure_file "backend/notifications/tests/test_sms_dispatch.py" "valid number -> 202 + taskId; invalid -> 400"
ensure_file "backend/notifications/tests/test_no_phone_persistence.py" "regression test: stored Notification never contains the phone number"
 
# ---- backend/common (new) -------------------------------------------------------
echo "-- backend/common/ --"
ensure_file "backend/common/__init__.py" "empty — marks common as a package"
ensure_file "backend/common/exceptions.py" "DRF exception handler -> standard { error: { code, message, details } } shape"
ensure_file "backend/common/pagination.py" "PageNumberPagination -> { data, pagination: { page, limit, total, totalPages } }"
ensure_file "backend/common/api_key_auth.py" "X-API-Key DRF authentication class for ATM-facing endpoints"
 
# ---- frontend/ (Admin Dashboard) -------------------------------------------------
echo "-- frontend/ --"
ensure_file "frontend/package.json" "react, react-router-dom, axios, zustand/redux-toolkit, lucide-react, Tailwind"
ensure_file "frontend/Dockerfile" "multi-stage: node build -> nginx serve"
ensure_file "frontend/.env.example" "VITE_API_BASE_URL, VITE_WS_URL"
ensure_file "frontend/src/services/api.js" "login, refreshToken, getATMs, getATMDetail, createATM, updateATM, getServices, getNotifications, getNetworkStats"
ensure_file "frontend/src/services/socket.js" "connect to VITE_WS_URL?token=..., dispatch atm.status.updated / atm.alert, reconnect logic"
ensure_file "frontend/src/store/atmsSlice.js" "{ atms, selectedATM, filters } + setATMs/updateATMStatus/selectATM/setFilters"
ensure_file "frontend/src/store/authSlice.js" "{ accessToken, refreshToken, role, isAuthenticated } + login/logout/refreshAccessToken"
ensure_file "frontend/src/pages/Login.jsx" "SCR-A1 — username/password form, calls api.login()"
ensure_file "frontend/src/pages/LiveMap.jsx" "SCR-A2 — KPI row, map + filters + list, opens ATM detail slide-over"
ensure_file "frontend/src/pages/Notifications.jsx" "SCR-A3 — notifications table with status/service filters"
ensure_file "frontend/src/utils/formatCurrency.js" "format current_cash_balance as EGP"
ensure_file "frontend/src/utils/formatDate.js" "ISO8601 -> relative time (e.g. '2 min ago')"
ensure_file "frontend/src/utils/statusMeta.js" "shared STATUS_META / NOTIF_META color+icon lookup"
ensure_empty_dir_marker "frontend/src/assets"
ensure_empty_dir_marker "frontend/src/components"
ensure_empty_dir_marker "frontend/src/__tests__/components"
ensure_empty_dir_marker "frontend/src/__tests__/services"
ensure_file "frontend/src/__tests__/components/ATMRow.test.jsx" "marker/row color matches status + cashStatus"
ensure_file "frontend/src/__tests__/services/api.test.js" "mocked fetch/axios sends correct Authorization / X-API-Key headers"
 
# ---- kiosk/ (new — Customer ATM screens) ------------------------------------------
echo "-- kiosk/ (new app) --"
ensure_file "kiosk/package.json" "react, zustand/context (no react-router-dom required — linear flow)"
ensure_file "kiosk/Dockerfile" "multi-stage: node build -> nginx serve"
ensure_file "kiosk/.env.example" "VITE_API_BASE_URL, VITE_ATM_API_KEY, VITE_ATM_ID"
ensure_file "kiosk/src/services/api.js" "attemptTransaction, getAlternatives, requestSms — all via X-API-Key, no JWT"
ensure_file "kiosk/src/store/sessionSlice.js" "in-memory only session state + resetSession() — never persisted, never stores phone number after send"
ensure_file "kiosk/src/pages/SelectService.jsx" "SCR-01 — service grid + amount pad (owner: عبدالله)"
ensure_file "kiosk/src/pages/CheckingStatus.jsx" "SCR-02 — loading/radar, <3s budget (owner: صفية)"
ensure_file "kiosk/src/pages/Unavailable.jsx" "SCR-03 — reason-based messaging: OFFLINE/MAINTENANCE/NO_CASH/INSUFFICIENT_CASH (owner: صفية)"
ensure_file "kiosk/src/pages/AlternativesList.jsx" "SCR-04 — top 3 alternatives, no real balance shown (owner: صفية)"
ensure_file "kiosk/src/pages/PhoneNumberEntry.jsx" "SCR-05 — phone input + skip link, clears state right after send (owner: محمد)"
ensure_file "kiosk/src/pages/Confirmation.jsx" "SCR-06 — success state + resetSession() (owner: محمد)"
ensure_file "kiosk/src/components/ServiceGrid.jsx" "service selection buttons"
ensure_file "kiosk/src/components/AmountPad.jsx" "requested amount input"
ensure_file "kiosk/src/components/StatusRadar.jsx" "loading/radar animation, reused by SCR-02"
ensure_file "kiosk/src/components/AlternativeCard.jsx" "branch name, distance, ETA, availability badge"
ensure_file "kiosk/src/components/PhoneInput.jsx" "phone number field"
ensure_file "kiosk/src/components/SuccessCheck.jsx" "success checkmark animation"
ensure_empty_dir_marker "kiosk/src/assets"
ensure_empty_dir_marker "kiosk/src/utils"
ensure_empty_dir_marker "kiosk/src/__tests__/pages"
ensure_file "kiosk/src/__tests__/pages/Unavailable.test.jsx" "each of the 4 reason values renders the right text/icon"
ensure_file "kiosk/src/__tests__/pages/PhoneNumberEntry.test.jsx" "phone number is cleared from state immediately after send"
 
echo
echo "== done =="
echo "  created: $CREATED"
echo "  already existed (skipped): $SKIPPED"
echo
echo "Run 'git status' to review, then commit."
 