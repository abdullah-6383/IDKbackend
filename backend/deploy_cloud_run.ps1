param(
  [Parameter(Mandatory=$true)] [string]$ProjectId,
  [Parameter(Mandatory=$true)] [string]$Region,
  [string]$RepoName = "idk-backend",
  [string]$ImageName = "backend",
  [string]$ServiceName = "idk-backend",
  [switch]$CreateSecrets,
  [string]$GoogleApiKey,
  [string]$SearchEngineId,
  [string]$FrontendOrigin
)

$ErrorActionPreference = "Stop"

Write-Host "Configuring gcloud project and region..." -ForegroundColor Cyan
gcloud config set project $ProjectId | Out-Null
gcloud config set run/region $Region | Out-Null

Write-Host "Enabling required services..." -ForegroundColor Cyan
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com | Out-Null

$repoPath = "$Region-docker.pkg.dev/$ProjectId/$RepoName"
$imageTag = "$repoPath/$ImageName:latest"

Write-Host "Ensuring Artifact Registry repository exists ($RepoName)..." -ForegroundColor Cyan
try {
  gcloud artifacts repositories describe $RepoName --location=$Region | Out-Null
} catch {
  gcloud artifacts repositories create $RepoName --repository-format=docker --location=$Region | Out-Null
}

Write-Host "Building and pushing image: $imageTag" -ForegroundColor Cyan
Push-Location $PSScriptRoot
try {
  gcloud builds submit --tag $imageTag
}
finally { Pop-Location }

Write-Host "Deploying Cloud Run service: $ServiceName" -ForegroundColor Cyan
$deployArgs = @(
  'run','deploy',$ServiceName,
  '--image', $imageTag,
  '--platform','managed',
  '--allow-unauthenticated',
  '--memory','1Gi',
  '--cpu','1',
  '--timeout','900',
  '--set-env-vars','PORT=8080'
)
if ($FrontendOrigin) {
  $deployArgs += @('--set-env-vars',"FRONTEND_ORIGIN=$FrontendOrigin")
}
# First deploy (env vars only)
gcloud @deployArgs

if ($CreateSecrets -and $GoogleApiKey -and $SearchEngineId) {
  Write-Host "Creating/updating secrets in Secret Manager..." -ForegroundColor Cyan
  try { gcloud secrets create GOOGLE_API_KEY --replication-policy=automatic | Out-Null } catch { }
  $tmp = New-TemporaryFile
  try {
    Set-Content -Path $tmp -NoNewline -Value $GoogleApiKey
    gcloud secrets versions add GOOGLE_API_KEY --data-file=$tmp | Out-Null
  } finally { Remove-Item -Force $tmp }

  try { gcloud secrets create SEARCH_ENGINE_ID --replication-policy=automatic | Out-Null } catch { }
  $tmp2 = New-TemporaryFile
  try {
    Set-Content -Path $tmp2 -NoNewline -Value $SearchEngineId
    gcloud secrets versions add SEARCH_ENGINE_ID --data-file=$tmp2 | Out-Null
  } finally { Remove-Item -Force $tmp2 }

  Write-Host "Updating service to mount secrets as environment variables..." -ForegroundColor Cyan
  gcloud run services update $ServiceName `
    --set-secrets GOOGLE_API_KEY=GOOGLE_API_KEY:latest,SEARCH_ENGINE_ID=SEARCH_ENGINE_ID:latest | Out-Null
}

Write-Host "Done. Fetching URL..." -ForegroundColor Cyan
gcloud run services describe $ServiceName --format='value(status.url)'
