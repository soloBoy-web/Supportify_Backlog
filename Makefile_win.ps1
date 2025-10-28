# Константы
$DockerComposeMain = "docker-compose.yml"
$EnvFile = ".env"
$VenvDir = ".venv"

# Docker команда
$DockerComposeCmd = "docker compose -f $DockerComposeMain --env-file $EnvFile"

task CleanEnv -Description "Clean virtual environment" {
    Write-Host "Cleaning virtual environment..." -ForegroundColor Yellow
    if (Test-Path $VenvDir) {
        Remove-Item -Recurse -Force $VenvDir
    }
}

task CreateEnv -Description "Create virtual environment" -Depends CleanEnv {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    python -m venv $VenvDir
}

task SyncAll -Description "Install dependencies" -Depends CreateEnv {
    Write-Host "Installing dependencies..." -ForegroundColor Green
    & "$VenvDir\Scripts\pip" install -r requirements.txt
}

task InitEnv -Description "Full initialization" -Depends CleanEnv, CreateEnv, SyncAll {
    Write-Host "Local environment is ready!" -ForegroundColor Cyan
}

task FixPermissions -Description "Fix permissions" {
    Write-Host "Fixing permissions..." -ForegroundColor Yellow
    if (Test-Path "prestart.sh") {
        icacls "prestart.sh" /grant:r "$env:USERNAME:(RX)"
    }
}

task RunService -Description "Run service" -Depends FixPermissions {
    Write-Host "Starting Docker Compose..." -ForegroundColor Cyan
    Invoke-Expression "$DockerComposeCmd up app -d --build"
}

task StopAll -Description "Stop all containers" {
    Write-Host "Stopping all containers..." -ForegroundColor Yellow
    $containers = docker ps -q
    if ($containers) {
        docker stop $containers
    }
    Write-Host "All containers stopped" -ForegroundColor Green
}

task StopAllAndRemove -Description "Stop and remove all containers" {
    Write-Host "Stopping and removing all containers..." -ForegroundColor Yellow
    $containers = docker ps -aq
    if ($containers) {
        docker stop $containers
        docker rm $containers
    }
    Write-Host "All containers removed" -ForegroundColor Green
}

task ShowGeneralSizeInfo -Description "Docker size info" {
    docker system df -v
}

task ShowContainersSize -Description "Containers size" {
    docker container ls -a -s --format "table {{.Names}}`t{{.Size}}"
}

task ShowImagesSize -Description "Images size" {
    docker image ls --format "table {{.Repository}}`t{{.Size}}"
}

task ShowDanglingImages -Description "Show dangling images" {
    docker images -f dangling=true
}

task DeleteDanglingImages -Description "Delete dangling images" {
    docker image prune -f
}

# Default task
task Default -Depends InitEnv