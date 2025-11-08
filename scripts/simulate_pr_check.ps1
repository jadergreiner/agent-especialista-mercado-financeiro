<#
Origin: DT-013 - Script de simulacao local para validar logica do workflow check-decisao.yml
Uso: powershell -ExecutionPolicy Bypass -File .\scripts\simulate_pr_check.ps1 .\scripts\demo_prs\pass.json
#>

Param(
    [Parameter(Mandatory=$true)]
    [string]$PayloadPath
)

if (-not (Test-Path $PayloadPath)) {
    Write-Error "Arquivo de payload nao encontrado: $PayloadPath"
    exit 2
}

try {
    $payload = Get-Content $PayloadPath -Raw | ConvertFrom-Json
} catch {
    Write-Error "Falha ao ler/parsear JSON: $_"
    exit 2
}

$changedFiles = @()
if ($payload.changedFiles) { $changedFiles = $payload.changedFiles }
$prBody = if ($payload.prBody) { $payload.prBody } else { "" }

# Definição simples dos paths sensíveis — manter em sincronia com .github/workflows/check-decisao.yml
$sensitivePaths = @(
    ".github/",
    "docs/governanca/",
    ".github/COPILOT_INSTRUCTIONS.md",
    "docs/gestao-agil/BACKLOG_DEBITO_TECNICO.md",
    ".github/workflows/"
)

$matchesSensitive = $false
foreach ($f in $changedFiles) {
    foreach ($p in $sensitivePaths) {
        if ($f -like "$p*") { $matchesSensitive = $true; break }
    }
    if ($matchesSensitive) { break }
}

if ($matchesSensitive) {
    if ($prBody -match "DECISAO-\d{3}") {
            Write-Output "APROVADO: PR contem referencia a decisao e arquivos sensiveis foram modificados."
        exit 0
    } else {
    Write-Output "REJEITADO: Arquivos sensiveis detectados, porem a PR NAO referencia 'DECISAO-XXX' no corpo."
        exit 1
    }
} else {
    Write-Output "APROVADO: Nenhum arquivo sensivel modificado."
    exit 0
}
