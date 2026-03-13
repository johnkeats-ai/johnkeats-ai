#!/bin/bash
set -e

PROJECT_ID="johnkeats-ai"
REGION="us-central1"
SERVICE_NAME="johnkeats-ai"
REPO_NAME="johnkeats-ai"
IMAGE_NAME="johnkeats-ai"

# Build
gcloud builds submit \
  --tag "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest" \
  . \
  --project=${PROJECT_ID}

# Deploy
gcloud run deploy ${SERVICE_NAME} \
  --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest" \
  --region=${REGION} \
  --allow-unauthenticated \
  --memory=1Gi \
  --timeout=300 \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION}" \
  --project=${PROJECT_ID}

echo "Deployed to: $(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)' --project=${PROJECT_ID})"
