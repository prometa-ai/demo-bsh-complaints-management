#!/bin/bash

# Setup script for Google Cloud Storage bucket for database persistence
# Usage: ./setup_gcs_bucket.sh PROJECT_ID BUCKET_NAME

PROJECT_ID=$1
BUCKET_NAME=$2

if [ -z "$PROJECT_ID" ] || [ -z "$BUCKET_NAME" ]; then
    echo "Usage: $0 PROJECT_ID BUCKET_NAME"
    echo "Example: $0 my-project-id bsh-complaints-db-bucket"
    exit 1
fi

echo "Setting up GCS bucket for database persistence..."
echo "Project ID: $PROJECT_ID"
echo "Bucket Name: $BUCKET_NAME"

# Set the project
gcloud config set project $PROJECT_ID

# Create the bucket
echo "Creating GCS bucket..."
gsutil mb gs://$BUCKET_NAME

# Set bucket permissions (private, only the service account can access)
echo "Setting bucket permissions..."
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME 2>/dev/null || true

# Enable versioning for backup safety
echo "Enabling versioning..."
gsutil versioning set on gs://$BUCKET_NAME

# Set lifecycle policy to keep only 10 versions
echo "Setting lifecycle policy..."
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "numNewerVersions": 10
        }
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://$BUCKET_NAME
rm lifecycle.json

echo "✅ GCS bucket setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure your Cloud Run service has Storage Admin permissions"
echo "2. Deploy with: GCS_BUCKET_NAME=$BUCKET_NAME"
echo ""
echo "Deploy command example:"
echo "gcloud builds submit --config cloudbuild.yaml \\"
echo "  --substitutions=_SERVICE_NAME=bsh-complaints,_DEPLOY_REGION=us-central1,_PLATFORM=managed,_AR_HOSTNAME=us-central1-docker.pkg.dev,_AR_REPO=your-repo,_SECRET_MANAGER_KEY=BSH_OPENAI_API_KEY,_GCP_PROJECT_ID=$PROJECT_ID,_GCS_BUCKET_NAME=$BUCKET_NAME"
