# Script para subir automáticamente cambios a GitHub
# git-quick-push.ps1

param(
    [string]$repoPath = ".",  # Ruta al repositorio, por defecto el directorio actual
    [string]$branch = "",     # Rama a la que subir (opcional, por defecto la rama actual)
    [string]$commitMessage = "" # Mensaje de commit (se pedirá si no se proporciona)
)

# Función para mostrar mensajes con colores
function Write-ColorMessage {
    param(
        [string]$message,
        [string]$color = "White"
    )
    Write-Host $message -ForegroundColor $color
}

# Cambiar al directorio del repositorio
Set-Location $repoPath
Write-ColorMessage "Trabajando en el repositorio: $repoPath" "Cyan"

# Verificar si estamos en un repositorio Git
if (-not (Test-Path ".git")) {
    Write-ColorMessage "Error: No estás en un repositorio Git." "Red"
    exit 1
}

# Obtener la rama actual si no se especificó
if ([string]::IsNullOrEmpty($branch)) {
    $branch = git rev-parse --abbrev-ref HEAD
    Write-ColorMessage "Usando la rama actual: $branch" "Yellow"
}

# Verificar si hay cambios para subir
$status = git status --porcelain
if ([string]::IsNullOrEmpty($status)) {
    Write-ColorMessage "No hay cambios para subir." "Yellow"
    exit 0
}

# Mostrar los archivos modificados
Write-ColorMessage "Archivos modificados:" "Cyan"
git status --short

# Solicitar el mensaje de commit si no se proporcionó
if ([string]::IsNullOrEmpty($commitMessage)) {
    $commitMessage = Read-Host -Prompt "Ingresa el mensaje de commit"
    if ([string]::IsNullOrEmpty($commitMessage)) {
        $commitMessage = "Actualización automática: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    }
}

# Preguntar si se quiere ver una diferencia detallada
$showDiff = Read-Host -Prompt "¿Quieres ver la diferencia detallada? (s/N)"
if ($showDiff.ToLower() -eq "s") {
    git diff
}

# Preguntar confirmación antes de continuar
$continue = Read-Host -Prompt "¿Continuar con la subida de los cambios? (S/n)"
if ($continue.ToLower() -eq "n") {
    Write-ColorMessage "Operación cancelada por el usuario." "Yellow"
    exit 0
}

# Añadir todos los cambios
Write-ColorMessage "Añadiendo todos los cambios..." "Green"
git add .

# Hacer commit con los cambios
Write-ColorMessage "Realizando commit con mensaje: $commitMessage" "Green"
git commit -m $commitMessage

# Subir los cambios a GitHub
Write-ColorMessage "Subiendo los cambios a la rama $branch en GitHub..." "Green"
git push origin $branch

# Verificar si la operación fue exitosa
if ($LASTEXITCODE -eq 0) {
    Write-ColorMessage "¡Cambios subidos exitosamente a GitHub!" "Green"
    Write-ColorMessage "Rama: $branch" "Cyan"
} else {
    Write-ColorMessage "Error al subir los cambios. Código de salida: $LASTEXITCODE" "Red"
}