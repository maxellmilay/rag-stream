#!/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS="key.json"

PROJECT_ID="rag-stream"
LOCATION="us-central1"
REPOSITORY="rag-stream"
IMAGE="rag-stream"
TAG="latest"

gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

gcloud config set project $PROJECT_ID

gcloud config set run/region $LOCATION

gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

IMAGE_NAME=$LOCATION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE
IMAGE_URI=$IMAGE_NAME:$TAG

docker build -t $IMAGE_URI .

docker push $IMAGE_URI

gcloud run deploy $REPOSITORY \
  --image=$IMAGE_URI \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=2G \
  --cpu=2
  