[CmdletBinding()]
param(
	[int]$MaxIterations = 10,
	[string]$StoryId,
	[string]$Model,
	[ValidateSet('low', 'medium', 'high', 'xhigh')]
	[string]$ReasoningEffort = 'high',
	[ValidateSet('workspace-write', 'danger-full-access')]
	[string]$Sandbox = 'workspace-write',
	[switch]$EnableSearch,
	[switch]$AutoCommit,
	[switch]$AllowDirtyWorktree,
	[switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptRoot = $PSScriptRoot
if (-not $scriptRoot) {
	$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $scriptRoot '..\..'))
$prdPath = Join-Path $scriptRoot 'prd.json'
$progressPath = Join-Path $scriptRoot 'progress.txt'
$eventsLogPath = Join-Path $scriptRoot 'events.log'
$runLogPath = Join-Path $scriptRoot 'run.log'
$lastMessagePath = Join-Path $scriptRoot 'last-message.md'
$promptPath = Join-Path $scriptRoot 'prompt.current.md'
$archiveRoot = Join-Path $scriptRoot 'archive'
$lastBranchPath = Join-Path $scriptRoot '.last-branch'
$instructionPath = Join-Path $scriptRoot 'CODEX.md'

function Write-EventLog {
	param(
		[string]$Message
	)

	$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
	$line = "[$timestamp] $Message"
	Write-Host $line
	Add-Content -Path $eventsLogPath -Value $line
}

function Get-PrdState {
	return Get-Content -Raw -Path $prdPath | ConvertFrom-Json -Depth 100
}

function Save-PrdState {
	param(
		[object]$Prd
	)

	$Prd | ConvertTo-Json -Depth 100 | Out-File -FilePath $prdPath -Encoding utf8
}

function Get-IncompleteStories {
	param(
		[object]$Prd
	)

	$stories = @($Prd.userStories | Where-Object { -not $_.passes })
	return $stories | Sort-Object @{ Expression = { [int]$_.priority } }, @{ Expression = { $_.id } }
}

function Get-SelectedStory {
	param(
		[object]$Prd,
		[string]$RequestedStoryId
	)

	if ($RequestedStoryId) {
		$requestedStory = @($Prd.userStories | Where-Object { $_.id -eq $RequestedStoryId }) | Select-Object -First 1
		if (-not $requestedStory) {
			throw "Story '$RequestedStoryId' was not found in $prdPath."
		}
		if ($requestedStory.passes) {
			throw "Story '$RequestedStoryId' is already marked passed in $prdPath."
		}
		return $requestedStory
	}

	return @(Get-IncompleteStories -Prd $Prd) | Select-Object -First 1
}

function Test-DirtyWorktree {
	param(
		[string]$Root
	)

	$status = & git -C $Root status --porcelain
	if ($LASTEXITCODE -ne 0) {
		throw 'git status failed.'
	}

	return -not [string]::IsNullOrWhiteSpace(($status | Out-String))
}

function Get-GitStatusText {
	param(
		[string]$Root
	)

	$status = & git -C $Root status --short
	if ($LASTEXITCODE -ne 0) {
		throw 'git status --short failed.'
	}
	if (-not $status) {
		return 'clean'
	}

	return ($status -join [Environment]::NewLine)
}

function Ensure-TargetBranch {
	param(
		[string]$Root,
		[string]$TargetBranch,
		[bool]$AllowDirty
	)

	if ([string]::IsNullOrWhiteSpace($TargetBranch)) {
		return
	}

	$currentBranch = (& git -C $Root branch --show-current).Trim()
	if ($LASTEXITCODE -ne 0) {
		throw 'Unable to determine current git branch.'
	}

	if ($currentBranch -eq $TargetBranch) {
		return
	}

	if ((Test-DirtyWorktree -Root $Root) -and -not $AllowDirty) {
		throw "Refusing to switch from '$currentBranch' to '$TargetBranch' on a dirty worktree. Re-run with -AllowDirtyWorktree if that is intentional."
	}

	$existingBranch = (& git -C $Root branch --list $TargetBranch | Out-String).Trim()
	if ($LASTEXITCODE -ne 0) {
		throw 'Unable to inspect existing git branches.'
	}

	if ($existingBranch) {
		& git -C $Root switch $TargetBranch
	} else {
		& git -C $Root switch -c $TargetBranch
	}

	if ($LASTEXITCODE -ne 0) {
		throw "Unable to switch to target branch '$TargetBranch'."
	}
}

function Initialize-ProgressLog {
	param(
		[object]$Prd
	)

	$lines = @(
		'# Ralph Progress Log',
		"Started: $(Get-Date -Format 'yyyy-MM-dd')",
		'Purpose: Repo-local Codex Ralph loop for Quake Live parity work.',
		"Target branch: $($Prd.branchName)",
		'---',
		'## Starter Checklist'
	)

	foreach ($story in ($Prd.userStories | Sort-Object @{ Expression = { [int]$_.priority } }, @{ Expression = { $_.id } })) {
		$lines += "- [ ] $($story.id): $($story.title)"
	}

	$lines += '---'
	$lines | Out-File -FilePath $progressPath -Encoding utf8
}

function Archive-RunStateIfBranchChanged {
	param(
		[object]$Prd
	)

	if (-not (Test-Path $lastBranchPath)) {
		if (-not [string]::IsNullOrWhiteSpace($Prd.branchName)) {
			$Prd.branchName | Out-File -FilePath $lastBranchPath -Encoding utf8
		}
		return
	}

	$previousBranch = (Get-Content -Raw -Path $lastBranchPath).Trim()
	$currentBranch = [string]$Prd.branchName
	if ([string]::IsNullOrWhiteSpace($previousBranch) -or [string]::IsNullOrWhiteSpace($currentBranch) -or $previousBranch -eq $currentBranch) {
		$currentBranch | Out-File -FilePath $lastBranchPath -Encoding utf8
		return
	}

	$timestamp = Get-Date -Format 'yyyy-MM-dd-HHmmss'
	$folderName = $previousBranch -replace '[:\\/ ]', '-'
	$archivePath = Join-Path $archiveRoot "$timestamp-$folderName"
	New-Item -ItemType Directory -Path $archivePath -Force | Out-Null

	if (Test-Path $prdPath) {
		Copy-Item -Path $prdPath -Destination (Join-Path $archivePath 'prd.json') -Force
	}
	if (Test-Path $progressPath) {
		Copy-Item -Path $progressPath -Destination (Join-Path $archivePath 'progress.txt') -Force
	}

	Write-EventLog "Archived previous Ralph state to $archivePath"
	Initialize-ProgressLog -Prd $Prd
	$currentBranch | Out-File -FilePath $lastBranchPath -Encoding utf8
}

function Build-IterationPrompt {
	param(
		[object]$Prd,
		[object]$Story,
		[int]$IterationNumber,
		[int]$IterationLimit,
		[string]$GitStatus,
		[bool]$CommitEnabled
	)

	$instructionText = Get-Content -Raw -Path $instructionPath
	$storyJson = $Story | ConvertTo-Json -Depth 30
	$verificationJson = $Prd.verificationCommands | ConvertTo-Json -Depth 20
	$commitMode = if ($CommitEnabled) { 'AUTO_COMMIT' } else { 'MANUAL_REVIEW' }

	return @"
$instructionText

## Runner Context

- Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Repo root: $repoRoot
- Iteration: $IterationNumber / $IterationLimit
- Commit mode: $commitMode
- Selected story id: $($Story.id)
- Selected story title: $($Story.title)

### Git Status At Iteration Start

```text
$GitStatus
```

### Verification Commands

```json
$verificationJson
```

### Selected Story

```json
$storyJson
```

## Runner Instructions

- Complete exactly one Ralph iteration for the selected story.
- If the story is too large for one iteration, split it into smaller stories in `.codex/ralph/prd.json`, update `.codex/ralph/progress.txt`, and stop.
- If commit mode is `AUTO_COMMIT`, create at most one commit after verification passes. If commit mode is `MANUAL_REVIEW`, do not create a commit.
- Keep the final response concise and status-oriented.
- Only emit `<promise>COMPLETE</promise>` on its own final line when `.codex/ralph/prd.json` has no remaining `passes: false` stories.
"@
}

if (-not (Test-Path $prdPath)) {
	throw "Missing PRD file: $prdPath"
}
if (-not (Test-Path $instructionPath)) {
	throw "Missing instruction file: $instructionPath"
}
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
	throw 'codex CLI was not found on PATH.'
}

$prd = Get-PrdState
Archive-RunStateIfBranchChanged -Prd $prd
if (-not (Test-Path $progressPath)) {
	Initialize-ProgressLog -Prd $prd
}

if ((Test-DirtyWorktree -Root $repoRoot) -and -not $AllowDirtyWorktree) {
	throw 'The git worktree is dirty. Re-run with -AllowDirtyWorktree if you want Ralph to operate on top of existing local changes.'
}

Ensure-TargetBranch -Root $repoRoot -TargetBranch $prd.branchName -AllowDirty:$AllowDirtyWorktree.IsPresent

if (Test-Path $runLogPath) {
	Remove-Item -Path $runLogPath -Force
}
if (Test-Path $eventsLogPath) {
	Remove-Item -Path $eventsLogPath -Force
}
if (Test-Path $lastMessagePath) {
	Remove-Item -Path $lastMessagePath -Force
}

Write-EventLog "Ralph starting in $repoRoot"
Write-EventLog "Target branch: $($prd.branchName)"
Write-EventLog "Commit mode: $(if ($AutoCommit) { 'auto' } else { 'manual' })"

for ($iteration = 1; $iteration -le $MaxIterations; $iteration++) {
	$prd = Get-PrdState
	$selectedStory = Get-SelectedStory -Prd $prd -RequestedStoryId $StoryId
	if (-not $selectedStory) {
		Write-EventLog 'All stories are already marked passed.'
		Write-Host '<promise>COMPLETE</promise>'
		exit 0
	}

	$gitStatus = Get-GitStatusText -Root $repoRoot
	$prompt = Build-IterationPrompt -Prd $prd -Story $selectedStory -IterationNumber $iteration -IterationLimit $MaxIterations -GitStatus $gitStatus -CommitEnabled:$AutoCommit.IsPresent
	$prompt | Out-File -FilePath $promptPath -Encoding utf8

	Write-EventLog "Iteration $iteration/$MaxIterations starting for $($selectedStory.id) - $($selectedStory.title)"

	if ($DryRun) {
		Write-EventLog 'Dry run enabled; prompt generated without invoking Codex.'
		exit 0
	}

	$codexArgs = @()
	if ($EnableSearch) {
		$codexArgs += '--search'
	}
	$codexArgs += '-a'
	$codexArgs += 'never'
	$codexArgs += 'exec'
	$codexArgs += '-C'
	$codexArgs += $repoRoot
	$codexArgs += '-s'
	$codexArgs += $Sandbox
	$codexArgs += '--color'
	$codexArgs += 'never'
	$codexArgs += '-o'
	$codexArgs += $lastMessagePath
	if ($Model) {
		$codexArgs += '-m'
		$codexArgs += $Model
	}
	$codexArgs += '-c'
	$codexArgs += "model_reasoning_effort=`"$ReasoningEffort`""
	$codexArgs += '-'

	Add-Content -Path $runLogPath -Value "===== Ralph iteration $iteration / $MaxIterations : $($selectedStory.id) ====="
	$null = Get-Content -Raw -Path $promptPath | & codex @codexArgs 2>&1 | Tee-Object -FilePath $runLogPath -Append
	if ($LASTEXITCODE -ne 0) {
		throw "codex exec failed during iteration $iteration."
	}

	$lastMessage = ''
	if (Test-Path $lastMessagePath) {
		$lastMessage = Get-Content -Raw -Path $lastMessagePath
	}

	$prdAfterIteration = Get-PrdState
	$remainingStories = @(Get-IncompleteStories -Prd $prdAfterIteration)
	if ($StoryId) {
		$targetStory = @($prdAfterIteration.userStories | Where-Object { $_.id -eq $StoryId }) | Select-Object -First 1
		if ($targetStory -and $targetStory.passes) {
			Write-EventLog "Requested story $StoryId is now marked passed."
			exit 0
		}
	}

	if ($lastMessage -match '<promise>COMPLETE</promise>') {
		Write-EventLog 'Codex signaled completion.'
		exit 0
	}

	if (-not $remainingStories) {
		Write-EventLog 'No remaining incomplete stories detected after iteration.'
		Write-Host '<promise>COMPLETE</promise>'
		exit 0
	}

	Write-EventLog "Iteration $iteration complete; $($remainingStories.Count) story or stories remain."
	Start-Sleep -Seconds 2
}

Write-EventLog "Reached max iterations ($MaxIterations) with incomplete stories remaining."
exit 1
