# scripts/validate_onboarding.ps1
# Script de validação de onboarding técnico para Agent Especialista Mercado Financeiro
# Executar em ambiente limpo (Windows PowerShell) para verificar setup básico

Write-Host "=== Validação de Onboarding Técnico ===" -ForegroundColor Green
Write-Host "Verificando ambiente de desenvolvimento..." -ForegroundColor Yellow

# 1. Verificar versão do Python
Write-Host "`n1. Verificando Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(11|12|13)") {
        Write-Host "✓ Python versão compatível: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Python versão não compatível. Necessário Python 3.11+." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Python não encontrado. Instalar Python 3.11+." -ForegroundColor Red
    exit 1
}

# 2. Verificar se virtualenv está ativa (opcional, mas recomendado)
Write-Host "`n2. Verificando virtualenv..." -ForegroundColor Cyan
if ($env:VIRTUAL_ENV) {
    Write-Host "✓ Virtualenv ativa: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "! Virtualenv não ativa. Recomendado ativar." -ForegroundColor Yellow
}

# 3. Instalar dependências (se requirements.txt existir)
Write-Host "`n3. Instalando dependências..." -ForegroundColor Cyan
$requirementsPath = "..\backend\requirements.txt"
if (Test-Path $requirementsPath) {
    try {
        pip install -r $requirementsPath --quiet
        Write-Host "✓ Dependências instaladas com sucesso." -ForegroundColor Green
    } catch {
        Write-Host "✗ Erro ao instalar dependências." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "! Arquivo requirements.txt não encontrado em $requirementsPath" -ForegroundColor Yellow
}

# 4. Verificar Docker e subir serviços (se docker-compose.yml existir)
Write-Host "`n4. Verificando Docker e serviços..." -ForegroundColor Cyan
$dockerComposePath = "..\docker-compose.yml"
if (Test-Path $dockerComposePath) {
    try {
        docker --version > $null 2>&1
        Write-Host "✓ Docker instalado." -ForegroundColor Green

        # Subir serviços em background
        Write-Host "Subindo serviços Docker (Postgres, Redis)..." -ForegroundColor Yellow
        docker compose -f $dockerComposePath up -d postgres redis
        Start-Sleep -Seconds 10  # Esperar inicialização

        # Verificar se containers estão rodando
        $containers = docker ps --filter "name=postgres" --filter "name=redis" --format "{{.Names}}"
        if ($containers -match "postgres" -and $containers -match "redis") {
            Write-Host "✓ Serviços Docker ativos: Postgres e Redis." -ForegroundColor Green
        } else {
            Write-Host "✗ Serviços Docker não iniciaram corretamente." -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "✗ Docker não encontrado ou erro ao subir serviços." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "! Arquivo docker-compose.yml não encontrado." -ForegroundColor Yellow
}

# 5. Rodar testes unitários rápidos
Write-Host "`n5. Executando testes unitários..." -ForegroundColor Cyan
try {
    # Assumir que estamos na pasta scripts, subir um nível para backend
    Set-Location "..\backend"
    pytest tests/unit -q --tb=short
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Testes unitários passaram." -ForegroundColor Green
    } else {
        Write-Host "✗ Alguns testes unitários falharam." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Erro ao executar testes (pytest não encontrado ou falha)." -ForegroundColor Red
    exit 1
}

# 6. Verificar endpoint básico (se aplicável)
Write-Host "`n6. Verificando endpoint de saúde..." -ForegroundColor Cyan
try {
    # Assumir que o app está rodando localmente na porta 8000 (ajustar se necessário)
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Endpoint /health respondendo corretamente." -ForegroundColor Green
    } else {
        Write-Host "✗ Endpoint /health não respondeu (Status: $($response.StatusCode))." -ForegroundColor Red
    }
} catch {
    Write-Host "! Endpoint /health não acessível (app não rodando ou porta errada)." -ForegroundColor Yellow
}

Write-Host "`n=== Validação Concluída ===" -ForegroundColor Green
Write-Host "Ambiente pronto para desenvolvimento!" -ForegroundColor Green
exit 0