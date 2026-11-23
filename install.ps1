# Install (or update) the Restaurant Health Report skill for Claude Code and Codex on Windows.
#   irm https://raw.githubusercontent.com/YangzhenRuan/restaurant-health-report/main/install.ps1 | iex
$ErrorActionPreference = "Stop"
$Repo = "YangzhenRuan/restaurant-health-report"
$Name = "restaurant-health-report"
$ClaudeDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
$CodexDir = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("rhr-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
  Write-Host "Downloading $Repo ..."
  $zip = Join-Path $tmp "repo.zip"
  Invoke-WebRequest -Uri "https://github.com/$Repo/archive/refs/heads/main.zip" -OutFile $zip -UseBasicParsing
  Expand-Archive -Path $zip -DestinationPath $tmp
  $src = Get-ChildItem -Path $tmp -Directory -Recurse | Where-Object { $_.Name -eq $Name -and $_.Parent.Name -eq "skills" } | Select-Object -First 1
  if (-not $src) { throw "Could not find skills/$Name in the download." }
  foreach ($base in @($ClaudeDir, $CodexDir)) {
    $dest = Join-Path $base "skills"
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    $target = Join-Path $dest $Name
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Copy-Item -Recurse -Path $src.FullName -Destination $target
    Write-Host "Installed: $target"
  }
} finally {
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
if (Get-Command python -ErrorAction SilentlyContinue) { Write-Host "Python: OK" } else { Write-Host "Python: missing. Install from python.org and tick 'Add python.exe to PATH'." }
Write-Host ""
Write-Host "Done. Restart Claude Code or Codex, then ask:"
Write-Host '  "Make a restaurant health report for <restaurant name>, <website or address>."'
