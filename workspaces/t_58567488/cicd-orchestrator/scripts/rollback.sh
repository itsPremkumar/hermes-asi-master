#!/usr/bin/env bash
# rollback.sh — Rollback to the opposite color in a blue-green deployment.
# Usage: ./rollback.sh <app-name> <namespace> <current-color>
set -euo pipefail

APP_NAME="${1:?Usage: rollback.sh <app-name> <namespace> <current-color>}"
NAMESPACE="${2:-default}"
CURRENT_COLOR="${3:?current color: blue or green}"

if [ "$CURRENT_COLOR" = "blue" ]; then
    TARGET="green"
else
    TARGET="blue"
fi

echo "Rolling back ${APP_NAME} from ${CURRENT_COLOR} to ${TARGET} in namespace ${NAMESPACE}"

# Switch service selector
kubectl patch svc "${APP_NAME}-service" -n "${NAMESPACE}" -p \
    "{\"spec\":{\"selector\":{\"app\":\"${APP_NAME}\",\"version\":\"${TARGET}\"}}}"

# Scale down the failed color
kubectl scale deployment "${APP_NAME}-${CURRENT_COLOR}" -n "${NAMESPACE}" --replicas=0

# Scale up the target if needed
CURRENT_REPLICAS=$(kubectl get deployment "${APP_NAME}-${TARGET}" -n "${NAMESPACE}" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
if [ "${CURRENT_REPLICAS}" = "0" ]; then
    kubectl scale deployment "${APP_NAME}-${TARGET}" -n "${NAMESPACE}" --replicas=2
fi

# Verify
echo "Waiting for rollout..."
kubectl rollout status deployment/"${APP_NAME}-${TARGET}" -n "${NAMESPACE}" --timeout=120s

echo "Rollback complete. Active color: ${TARGET}"
kubectl get pods -n "${NAMESPACE}" -l "app=${APP_NAME}"