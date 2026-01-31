<#
pcap-to-edges.ps1
Windows PowerShell script to parse a PCAP/PCAPNG into an IPv4 IP-to-IP edge list using tshark.

What it does (one run):
- Asks for PCAP path (drag-drop supported)
- Finds tshark.exe automatically (PATH or default install paths) or asks you
- Uses capinfos.exe (if available) to compute % progress
- Extracts IPv4 src/dst pairs (fast StreamWriter, no per-line Add-Content)
- Produces:
    pairs.csv                (src_ip,dst_ip)
    edges.csv                (count,src_ip,dst_ip) directional
    edges_undirected.csv     (count,ip_a,ip_b) undirected A<->B merged
- Prints live progress and a top-10 summary

Requirements:
- Wireshark installed (tshark.exe present). capinfos.exe is optional but recommended.

Run:
  Set-ExecutionPolicy -Scope Process Bypass
  .\pcap-to-edges.ps1
#>

$ErrorActionPreference = "Stop"

function Find-Tshark {
  $cmd = Get-Command tshark -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }

  $candidates = @(
    "C:\Program Files\Wireshark\tshark.exe",
    "C:\Program Files (x86)\Wireshark\tshark.exe"
  )
  foreach ($p in $candidates) {
    if (Test-Path $p) { return $p }
  }

  Write-Host ""
  Write-Host "Couldn't find tshark.exe automatically." -ForegroundColor Yellow
  $manual = Read-Host "Enter full path to tshark.exe (e.g. C:\Program Files\Wireshark\tshark.exe)"
  $manual = $manual.Trim('"')
  if (Test-Path $manual) { return $manual }

  throw "tshark.exe not found. Install Wireshark or provide a valid path."
}

function Find-Capinfos([string]$tsharkPath) {
  $dir = Split-Path $tsharkPath
  $cap = Join-Path $dir "capinfos.exe"
  if (Test-Path $cap) { return $cap }

  $fallback = @(
    "C:\Program Files\Wireshark\capinfos.exe",
    "C:\Program Files (x86)\Wireshark\capinfos.exe"
  )
  foreach ($p in $fallback) {
    if (Test-Path $p) { return $p }
  }
  return $null
}

function Nice-Count([long]$n) { return "{0:n0}" -f $n }

Write-Host "=== PCAP -> IP Edge List (IPv4) ===" -ForegroundColor Cyan
Write-Host ""

# --- Input: PCAP path ---
$pcap = Read-Host "Enter path to PCAP/PCAPNG (or drag-drop it here)"
$pcap = $pcap.Trim().Trim('"')

if (-not (Test-Path $pcap)) {
  throw "PCAP file not found: $pcap"
}

# --- Input: output folder ---
$outDir = Read-Host "Output folder (Enter for current folder)"
$outDir = $outDir.Trim().Trim('"')
if ([string]::IsNullOrWhiteSpace($outDir)) { $outDir = (Get-Location).Path }
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

# --- Resolve tshark/capinfos ---
$tshark = Find-Tshark
$capinfos = Find-Capinfos $tshark

Write-Host ""
Write-Host "Using tshark: $tshark" -ForegroundColor DarkGray
Write-Host "PCAP:        $pcap" -ForegroundColor DarkGray
Write-Host "Output:      $outDir" -ForegroundColor DarkGray
if ($capinfos) { Write-Host "capinfos:    $capinfos" -ForegroundColor DarkGray } else { Write-Host "capinfos:    (not found; % progress disabled)" -ForegroundColor DarkGray }
Write-Host ""

# --- Output filenames ---
$pairsPath  = Join-Path $outDir "pairs.csv"
$edgesPath  = Join-Path $outDir "edges.csv"
$uedgesPath = Join-Path $outDir "edges_undirected.csv"

# --- Data structures ---
$dirCounts   = New-Object "System.Collections.Generic.Dictionary[string,int64]"
$undirCounts = New-Object "System.Collections.Generic.Dictionary[string,int64]"
$ipSeen      = New-Object "System.Collections.Generic.HashSet[string]"

[long]$totalPkts = 0
if ($capinfos) {
  try {
    # capinfos output includes: "Number of packets:   12345"
    $line = & $capinfos -c $pcap | Select-String "Number of packets"
    if ($line) { $totalPkts = [int64]($line.ToString() -replace '.*:\s*','') }
  } catch {
    $totalPkts = 0
  }
}

# --- Counters ---
[long]$totalLines = 0
[long]$keptPairs  = 0

# =========================
# Stage 1/3: Extraction
# =========================
Write-Host "Stage 1/3: Extracting IPv4 src/dst pairs..." -ForegroundColor Green
if ($totalPkts -gt 0) {
  Write-Host "  Total packets (capinfos): $totalPkts" -ForegroundColor DarkGray
} else {
  Write-Host "  Total packets unknown (capinfos missing or unreadable). Showing counts only." -ForegroundColor Yellow
}
Write-Host "  Tip: -n disables name resolution for speed." -ForegroundColor DarkGray
Write-Host ""

# FAST write: keep file handle open
$pairsWriter = New-Object System.IO.StreamWriter($pairsPath, $false, [System.Text.Encoding]::ASCII)
$pairsWriter.WriteLine("src_ip,dst_ip")

# Start tshark as a process to stream stdout efficiently
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $tshark
$psi.Arguments = "-n -r `"$pcap`" -Y ip -T fields -E header=n -E separator=/t -E quote=n -e frame.number -e ip.src -e ip.dst"
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError  = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true

$p = New-Object System.Diagnostics.Process
$p.StartInfo = $psi
[void]$p.Start()

$stdout = $p.StandardOutput
$stderr = $p.StandardError

$lastUpdate = Get-Date
$updateEverySeconds = 1
[long]$lastFrameNo = 0

while (-not $stdout.EndOfStream) {
  $line = $stdout.ReadLine()
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $totalLines++

  # Expect: frameNo<TAB>src<TAB>dst
  $parts = $line.Split("`t")
  if ($parts.Count -lt 3) { continue }

  # Parse
  $frameNo = 0
  [void][int64]::TryParse($parts[0], [ref]$frameNo)
  $src = $parts[1]
  $dst = $parts[2]

  # Fast IPv4 sanity (avoid expensive regex)
  if ($src.IndexOf('.') -lt 0 -or $dst.IndexOf('.') -lt 0) { continue }
  if ($src.Length -lt 7 -or $dst.Length -lt 7) { continue }

  $keptPairs++
  $lastFrameNo = $frameNo

  # Track IPs
  $null = $ipSeen.Add($src)
  $null = $ipSeen.Add($dst)

  # Write pair
  $pairsWriter.WriteLine("$src,$dst")

  # Directional count
  $k = "$src|$dst"
  if ($dirCounts.ContainsKey($k)) { $dirCounts[$k]++ } else { $dirCounts[$k] = 1 }

  # Undirected count (sorted)
  $a = $src; $b = $dst
  if ([string]::CompareOrdinal($a,$b) -gt 0) { $t=$a; $a=$b; $b=$t }
  $uk = "$a|$b"
  if ($undirCounts.ContainsKey($uk)) { $undirCounts[$uk]++ } else { $undirCounts[$uk] = 1 }

  # Progress update (once per second)
  $now = Get-Date
  if (($now - $lastUpdate).TotalSeconds -ge $updateEverySeconds) {
    $lastUpdate = $now

    $status = "Frame $frameNo" +
              ($(if ($totalPkts -gt 0) { "/$totalPkts" } else { "" })) +
              " | pairs $(Nice-Count $keptPairs) | IPs $(Nice-Count $($ipSeen.Count)) | edges $(Nice-Count $($dirCounts.Count))"

    if ($totalPkts -gt 0 -and $frameNo -gt 0) {
      $pct = [math]::Min(100, [math]::Round(($frameNo / $totalPkts) * 100, 1))
      Write-Progress -Activity "Parsing PCAP" -Status $status -PercentComplete $pct
    } else {
      Write-Progress -Activity "Parsing PCAP" -Status $status -PercentComplete 0
    }
  }
}

$p.WaitForExit()
$pairsWriter.Flush()
$pairsWriter.Close()
Write-Progress -Activity "Parsing PCAP" -Completed

$errText = $stderr.ReadToEnd()
if ($p.ExitCode -ne 0) {
  throw "tshark failed (exit $($p.ExitCode)): $errText"
}

Write-Host "Extraction complete." -ForegroundColor Green
Write-Host ("  Lines read:       {0}" -f (Nice-Count $totalLines)) -ForegroundColor DarkGray
Write-Host ("  IPv4 pairs kept:  {0}" -f (Nice-Count $keptPairs)) -ForegroundColor DarkGray
Write-Host ("  Unique IPs:       {0}" -f (Nice-Count $ipSeen.Count)) -ForegroundColor DarkGray
Write-Host ("  Directed edges:   {0}" -f (Nice-Count $dirCounts.Count)) -ForegroundColor DarkGray
Write-Host ("  Undirected edges: {0}" -f (Nice-Count $undirCounts.Count)) -ForegroundColor DarkGray
Write-Host ""

# =========================
# Stage 2/3: edges.csv (directional)
# =========================
Write-Host "Stage 2/3: Writing edges.csv (directional counts)..." -ForegroundColor Green
"count,src_ip,dst_ip" | Out-File -Encoding ascii $edgesPath

$dirCounts.GetEnumerator() |
  Sort-Object Value -Descending |
  ForEach-Object {
    $parts = $_.Key.Split("|", 2)
    "{0},{1},{2}" -f $_.Value, $parts[0], $parts[1]
  } | Add-Content -Encoding ascii $edgesPath

Write-Host "  Wrote: $edgesPath" -ForegroundColor DarkGray
Write-Host ""

# =========================
# Stage 3/3: edges_undirected.csv
# =========================
Write-Host "Stage 3/3: Writing edges_undirected.csv (A<->B merged)..." -ForegroundColor Green
"count,ip_a,ip_b" | Out-File -Encoding ascii $uedgesPath

$undirCounts.GetEnumerator() |
  Sort-Object Value -Descending |
  ForEach-Object {
    $parts = $_.Key.Split("|", 2)
    "{0},{1},{2}" -f $_.Value, $parts[0], $parts[1]
  } | Add-Content -Encoding ascii $uedgesPath

Write-Host "  Wrote: $uedgesPath" -ForegroundColor DarkGray
Write-Host ""

# =========================
# Nice finish: Top talkers
# =========================
Write-Host "Top 10 directed connections (count src -> dst):" -ForegroundColor Cyan
$top10 = $dirCounts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 10
$i = 1
foreach ($e in $top10) {
  $p2 = $e.Key.Split("|",2)
  Write-Host ("  {0,2}. {1,8}  {2} -> {3}" -f $i, (Nice-Count $e.Value), $p2[0], $p2[1])
  $i++
}

Write-Host ""
Write-Host "All done ✅" -ForegroundColor Cyan
Write-Host "Files created:" -ForegroundColor Cyan
Write-Host "  $pairsPath"
Write-Host "  $edgesPath"
Write-Host "  $uedgesPath"
