[CmdletBinding()]
param(
    [switch]$StartSupabase,
    [switch]$SkipQuality,
    [switch]$SkipDatabase
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$evidenceRoot = $PSScriptRoot
$repoRoot = [IO.Path]::GetFullPath((Join-Path $evidenceRoot "..\..\..\..\.."))
$activeCardPath = Join-Path $repoRoot "tasks\active\1.3-durable-submit-fake-venue.yaml"
$completedCardPath = Join-Path $repoRoot "tasks\completed\1.3-durable-submit-fake-venue.yaml"
$cardPath = if (Test-Path -LiteralPath $activeCardPath) { $activeCardPath } else { $completedCardPath }
$results = [System.Collections.Generic.List[object]]::new()

function Add-Check {
    param(
        [string]$Id,
        [ValidateSet("PASS", "INFO", "BLOCKED", "FAIL")]
        [string]$Status,
        [string]$Detail
    )

    $results.Add([pscustomobject]@{
            id = $Id
            status = $Status
            detail = $Detail
        })
    Write-Output ("[{0}] {1}: {2}" -f $Status, $Id, $Detail)
}

function Invoke-Check {
    param(
        [string]$Id,
        [string]$Command,
        [string[]]$Arguments,
        [switch]$Diagnostic
    )

    $previousErrorAction = $ErrorActionPreference
    $exitCode = 1
    $commandOutput = @()
    try {
        $ErrorActionPreference = "Continue"
        $commandOutput = @(& $Command @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    catch {
        $exitCode = 1
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
    }

    if ($exitCode -eq 0) {
        Add-Check $Id "PASS" "exit=0"
    }
    else {
        if ($Diagnostic -and $commandOutput.Count -gt 0) {
            $diagnosticText = (($commandOutput | Select-Object -Last 3) -join " ").Trim()
            Add-Check $Id "FAIL" ("exit={0}; {1}" -f $exitCode, $diagnosticText)
        }
        else {
            Add-Check $Id "FAIL" ("exit={0}" -f $exitCode)
        }
    }
}

function Invoke-PythonStdinCheck {
    param(
        [string]$Id,
        [string]$Code
    )

    $previousErrorAction = $ErrorActionPreference
    $exitCode = 1
    $commandOutput = @()
    try {
        $ErrorActionPreference = "Continue"
        $commandOutput = @($Code | & uv run python - 2>&1)
        $exitCode = $LASTEXITCODE
    }
    catch {
        $exitCode = 1
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
    }

    if ($exitCode -eq 0) {
        Add-Check $Id "PASS" "exit=0"
    }
    else {
        $diagnosticText = (($commandOutput | Select-Object -Last 3) -join " ").Trim()
        Add-Check $Id "FAIL" ("exit={0}; {1}" -f $exitCode, $diagnosticText)
    }
}

function Get-CardList {
    param([string]$Section)

    $items = [System.Collections.Generic.List[string]]::new()
    $inside = $false
    foreach ($line in Get-Content -LiteralPath $cardPath) {
        if ($line -eq ("{0}:" -f $Section)) {
            $inside = $true
            continue
        }
        if ($inside -and $line -match "^[^\s].*:") {
            break
        }
        if ($inside -and $line -match '^\s+-\s+"([^"]+)"') {
            $items.Add($Matches[1])
        }
    }
    return $items
}

function Test-RepoGlob {
    param(
        [string]$Path,
        [string]$Pattern
    )

    $escaped = [regex]::Escape($Pattern)
    $escaped = $escaped.Replace("\*\*", ".*").Replace("\*", "[^/]*")
    return $Path -match ("^{0}$" -f $escaped)
}

Push-Location $repoRoot
try {
    $runUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Add-Check "run" "INFO" $runUtc

    $branch = (& git branch --show-current).Trim()
    if ($branch -match '^task/1\.3-') {
        Add-Check "branch" "PASS" $branch
    }
    else {
        Add-Check "branch" "FAIL" ("unexpected branch: {0}" -f $branch)
    }

    $statusLine = Select-String -LiteralPath $cardPath -Pattern '^status:\s*"([^"]+)"$'
    $cardStatus = $statusLine.Matches[0].Groups[1].Value
    if ($cardStatus -in @("READY", "IN_PROGRESS", "REVIEW", "DONE")) {
        Add-Check "task-card-status" "PASS" $cardStatus
    }
    else {
        Add-Check "task-card-status" "BLOCKED" ("canonical card is {0}; Account Owner transition required" -f $cardStatus)
    }

    $cardText = Get-Content -Raw -LiteralPath $cardPath
    $requiredCardFields = @(
        "task_id", "phase", "status", "owner", "reviewer", "expiry_at",
        "branch_pattern", "references", "goal", "non_goals", "preconditions",
        "blockers", "allowed_globs", "forbidden_globs", "impact",
        "acceptance_criteria", "required_commands", "evidence_path",
        "gate_impact", "rollback_or_forward_fix", "known_risks", "waiver_id"
    )
    $missingCardFields = @($requiredCardFields | Where-Object {
            $cardText -notmatch ("(?m)^\s*{0}:" -f [regex]::Escape($_))
        })
    if ($missingCardFields.Count -eq 0) {
        Add-Check "task-card-structure" "PASS" ("{0} required fields present" -f $requiredCardFields.Count)
    }
    else {
        Add-Check "task-card-structure" "FAIL" ("missing: {0}" -f ($missingCardFields -join ", "))
    }

    $changedFiles = @(& git status --porcelain | ForEach-Object {
            if ($_ -match '^..\s+(.+)$') { $Matches[1].Replace("\", "/") }
        })
    if ($changedFiles.Count -eq 0) {
        Add-Check "worktree" "PASS" "clean"
    }
    else {
        Add-Check "worktree" "INFO" ("{0} local change(s); commit or stash before implementation" -f $changedFiles.Count)
    }

    Invoke-Check "diff-check" "git" @("diff", "--check")

    $whitespaceHits = [System.Collections.Generic.List[string]]::new()
    foreach ($path in $changedFiles) {
        $fullPath = Join-Path $repoRoot $path
        if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) { continue }
        $lineNumber = 0
        foreach ($line in Get-Content -LiteralPath $fullPath) {
            $lineNumber++
            if ($line -match '\S[ \t]+$') {
                $whitespaceHits.Add("{0}:{1}" -f $path, $lineNumber)
            }
        }
    }
    if ($whitespaceHits.Count -eq 0) {
        Add-Check "changed-file-whitespace" "PASS" "no trailing whitespace in local changes"
    }
    else {
        Add-Check "changed-file-whitespace" "FAIL" ($whitespaceHits -join ", ")
    }

    $allowed = @(Get-CardList "allowed_globs")
    $forbidden = @(Get-CardList "forbidden_globs")
    $scopeViolations = [System.Collections.Generic.List[string]]::new()
    foreach ($path in $changedFiles) {
        $isAllowed = $false
        foreach ($pattern in $allowed) {
            if (Test-RepoGlob $path $pattern) { $isAllowed = $true; break }
        }
        foreach ($pattern in $forbidden) {
            if (Test-RepoGlob $path $pattern) { $isAllowed = $false; break }
        }
        if (-not $isAllowed) { $scopeViolations.Add($path) }
    }
    if ($scopeViolations.Count -eq 0) {
        Add-Check "allowlist" "PASS" "changed paths are within the task allowlist"
    }
    else {
        Add-Check "allowlist" "FAIL" ("out-of-scope: {0}" -f ($scopeViolations -join ", "))
    }

    $requiredPaths = @(
        "AI_AUTO_TRADE_MASTER_SPEC.md",
        "AGENTS.md",
        "contracts/commands/execution/submit-order.v1.schema.json",
        "contracts/events/execution/order-event.v1.schema.json",
        "contracts/config/task-card.v1.schema.json",
        "contracts/fixtures/submit-order.v1.valid.json",
        "contracts/fixtures/order-event.v1.valid.json",
        "scripts/validate_contracts.py",
        "docs/backend/adr/0002-hexagonal-architecture.md",
        "docs/backend/adr/0004-outbox-inbox-delivery.md",
        "docs/backend/adr/0005-canonical-oms.md",
        "docs/backend/adr/0007-risk-kill-switch-reconciliation.md",
        "docs/backend/adr/0012-transaction-concurrency.md",
        "docs/backend/adr/0014-toolchain-repo-contract-authority.md",
        "docs/governance/evidence/tasks/1.3/approval-record-2026-08-12.md",
        "docs/governance/evidence/tasks/1.3/risk-profile.local-simulator.v1.approved.json",
        "docs/governance/evidence/tasks/1.3/fake-venue-scenario.v1.schema.json",
        "docs/governance/evidence/tasks/1.3/fake-venue-scenario.v1.valid.json"
    )
    $missingPaths = @($requiredPaths | Where-Object { -not (Test-Path -LiteralPath (Join-Path $repoRoot $_)) })
    if ($missingPaths.Count -eq 0) {
        Add-Check "required-artifacts" "PASS" ("{0} paths present" -f $requiredPaths.Count)
    }
    else {
        Add-Check "required-artifacts" "FAIL" ("missing: {0}" -f ($missingPaths -join ", "))
    }

    $scenarioValidation = @'
import json
from pathlib import Path
from jsonschema import Draft202012Validator

root = Path.cwd()
schema = json.loads((root / "docs/governance/evidence/tasks/1.3/fake-venue-scenario.v1.schema.json").read_text())
fixture = json.loads((root / "docs/governance/evidence/tasks/1.3/fake-venue-scenario.v1.valid.json").read_text())
Draft202012Validator(schema).validate(fixture)
'@
    Invoke-PythonStdinCheck "scenario-fixture" $scenarioValidation
    Invoke-Check "contract-schemas" "uv" @("run", "python", "scripts/validate_contracts.py")

    $approvedFixture = Join-Path $repoRoot "docs\governance\evidence\tasks\1.3\risk-profile.local-simulator.v1.approved.json"
    $fixtureJson = Get-Content -Raw -LiteralPath $approvedFixture | ConvertFrom-Json
    if ($fixtureJson.status -eq "APPROVED" -and $fixtureJson.approval.policy_hash -match '^[0-9a-f]{64}$') {
        $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $approvedFixture).Hash.ToLowerInvariant()
        Add-Check "risk-fixture" "PASS" ("status=APPROVED; file_sha256={0}" -f $hash)
    }
    else {
        Add-Check "risk-fixture" "FAIL" "approved fixture metadata is invalid"
    }

    if (-not $SkipQuality) {
        Invoke-Check "uv-lock" "uv" @("sync", "--locked")
        Invoke-Check "ruff-format" "uv" @("run", "ruff", "format", "--check", ".")
        Invoke-Check "ruff-check" "uv" @("run", "ruff", "check", ".")
        Invoke-Check "pyright" "uv" @("run", "pyright")
        Invoke-Check "pytest" "uv" @("run", "pytest", "-q")
    }
    else {
        Add-Check "quality" "INFO" "skipped by switch"
    }

    if (-not $SkipDatabase) {
        $dockerExit = 0
        $null = & docker info 2>&1
        $dockerExit = $LASTEXITCODE
        if ($dockerExit -ne 0) {
            Add-Check "docker" "BLOCKED" "Docker daemon is unavailable"
        }
        else {
            Add-Check "docker" "PASS" "daemon available"
            if ($StartSupabase) {
                Invoke-Check "supabase-start" "npx" @("--yes", "supabase@2.113.0", "start")
            }

            $savedDatabaseUrl = $env:DATABASE_URL
            try {
                if ([string]::IsNullOrWhiteSpace($env:DATABASE_URL)) {
                    $statusAction = $ErrorActionPreference
                    try {
                        $ErrorActionPreference = "Continue"
                        $statusOutput = @(& npx --yes supabase@2.113.0 status -o env 2>&1)
                    }
                    catch {
                        $statusOutput = @()
                    }
                    finally {
                        $ErrorActionPreference = $statusAction
                    }
                    $dbLine = $statusOutput | Where-Object { $_ -match '^DB_URL=' } | Select-Object -First 1
                    if ($dbLine) {
                        $env:DATABASE_URL = ($dbLine -replace '^DB_URL=', '').Trim("'").Trim('"')
                    }
                }

                if ([string]::IsNullOrWhiteSpace($env:DATABASE_URL)) {
                    Add-Check "database-url" "BLOCKED" "DATABASE_URL unavailable"
                }
                else {
                    Add-Check "database-url" "PASS" "available in process only"
                    Invoke-Check "postgres-integration" "uv" @("run", "pytest", "tests/integration", "-q")
                    Invoke-Check "pytest-with-db" "uv" @("run", "pytest", "-q")
                    $taskTest = Join-Path $repoRoot "tests\integration\test_task_1_3_postgres.py"
                    if (Test-Path -LiteralPath $taskTest) {
                        Invoke-Check "task-1.3-postgres" "uv" @("run", "pytest", "tests/integration/test_task_1_3_postgres.py", "-q")
                    }
                    else {
                        Add-Check "task-1.3-postgres" "INFO" "not created yet; expected after READY and implementation"
                    }
                }
            }
            finally {
                $env:DATABASE_URL = $savedDatabaseUrl
            }
        }
    }
    else {
        Add-Check "database" "INFO" "skipped by switch"
    }

    $trackedTextFiles = @(git ls-files | Where-Object { $_ -match '\.(md|json|yaml|yml|py|toml|ps1)$' })
    $secretFiles = @()
    $placeholderFiles = @()
    foreach ($file in $trackedTextFiles) {
        $fullPath = Join-Path $repoRoot $file
        if (-not (Test-Path -LiteralPath $fullPath)) { continue }
        $hits = @(Select-String -LiteralPath $fullPath -Pattern 'sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]+ PRIVATE KEY-----|postgres(?:ql)?(?:\+[A-Za-z0-9]+)?://[^\s:@]+:[^\s@]+@')
        if ($hits.Count -eq 0) { continue }
        $nonPlaceholder = @($hits | Where-Object {
                $_.Line -notmatch 'changeme_local|<redacted>|example|placeholder'
            })
        if ($nonPlaceholder.Count -gt 0) {
            $secretFiles += $file
        }
        else {
            $placeholderFiles += $file
        }
    }
    if ($secretFiles.Count -eq 0) {
        Add-Check "secret-scan" "PASS" "no high-confidence secret pattern in tracked text files"
    }
    else {
        Add-Check "secret-scan" "FAIL" ("matches in: {0}" -f ($secretFiles -join ", "))
    }
    if ($placeholderFiles.Count -gt 0) {
        Add-Check "placeholder-credential-scan" "INFO" ("local placeholder only: {0}; do not use for external services" -f ($placeholderFiles -join ", "))
    }

    $blocked = @($results | Where-Object { $_.status -in @("FAIL", "BLOCKED") })
    Write-Output ""
    Write-Output ("Summary: PASS={0} INFO={1} BLOCKED={2} FAIL={3}" -f `
        @($results | Where-Object status -eq "PASS").Count,
        @($results | Where-Object status -eq "INFO").Count,
        @($results | Where-Object status -eq "BLOCKED").Count,
        @($results | Where-Object status -eq "FAIL").Count)

    if ($blocked.Count -gt 0) {
        exit 2
    }
}
finally {
    Pop-Location
}
