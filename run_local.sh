#!/bin/bash
SERVER_PORT=${1-5000}
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_USER=dhos-audit-api
export DATABASE_PASSWORD=dhos-audit-api
export DATABASE_NAME=dhos-audit-api
export SERVER_PORT=${SERVER_PORT}
export ENVIRONMENT=DEVELOPMENT
export ALLOW_DROP_DATA=true
export FLASK_APP=dhos_audit_api/autoapp.py
export HS_KEY=secret
export PROXY_URL=http://localhost/
export IGNORE_JWT_VALIDATION=true
export AUTH0_DOMAIN=https://login-sandbox.sensynehealth.com/
export AUTH0_AUDIENCE=https://dev.sensynehealth.com/
export AUTH0_METADATA=https://gdm.sensynehealth.com/metadata
export AUTH0_JWKS_URL=https://login-sandbox.sensynehealth.com/.well-known/jwks.json
export AUTH0_CUSTOM_DOMAIN=dev
export RABBITMQ_TEST=true
export RABBITMQ_NOENCRYPT=true
export REDIS_INSTALLED=False
export LOG_LEVEL=${LOG_LEVEL:-DEBUG}
export LOG_FORMAT=${LOG_FORMAT:-COLOUR}

if [ -z "$*" ]
then
  flask db upgrade
  python3 -m dhos_audit_api
else
  flask $*
fi
