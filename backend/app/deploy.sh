#!/bin/bash

# Configuration
PROJECT_ID="johnkeats-ai"
REGION="us-central1"
SERVICE_NAME="johnkeats-ai"
IMAGE_NAME="us-central1-docker.pkg.dev/${PROJECT_ID}/app-repo/${SERVICE_NAME}"

echo "🚀 Starting deployment for ${SERVICE_NAME}..."

# Build the image using Cloud Build
echo "📦 Building container image..."
gcloud builds submit --tag ${IMAGE_NAME} --project ${PROJECT_ID} .

# Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},KEATS_MODEL=gemini-live-2.5-flash-native-audio,KEATS_VOICE_NAME=Achird,APP_NAME=johnkeats-ai"

echo "✅ Deployment complete!"
gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --project ${PROJECT_ID} --format 'value(status.url)'
