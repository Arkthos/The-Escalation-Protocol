# Diagnosing Microsoft Defender Endpoint ECS Connectivity Issues

## Summary

This article provides a PowerShell-based diagnostic approach to validate and capture telemetry for **Microsoft Defender for Endpoint's ECS (Endpoint Configuration Service)** connectivity. It includes a script that collects connection test results, logs, and a network capture to assist with troubleshooting ECS reachability issues, which are **not currently covered by MDE Client Analyzer (MDECA)**.

---

## What is ECS?

**ECS (Endpoint Configuration Service)** is a Microsoft cloud service used by Windows Defender and Microsoft Defender for Endpoint (MDE) clients to retrieve configuration data such as feature flags, diagnostic settings, and platform behavior instructions. ECS URLs are dynamically assigned and can vary based on region, tenant, or client configuration. [Microsoft Defender Core Service Overview](https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-core-service-overview)


---

## Problem

When investigating MDE client issues related to cloud configuration, ECS connectivity is a potential blind spot. **MDE Client Analyzer (MDECA)** currently **does not validate ECS URL reachability**, and failures in ECS communication can lead to:

- Missing or stale Defender configurations
- Delayed or absent feature rollouts
- Unexpected protection behavior

---

## Objective

Provide a diagnostic script that:

- Automatically discovers the ECS endpoint URL on the local device
- Validates basic connectivity (DNS, port, proxy)
- Attempts an HTTPS request to the ECS configuration URL
- Collects response headers and logs success/failure
- Captures network traffic to an `.etl` file
- Exports a full diagnostic report to the desktop

---

## Prerequisites

- Windows PowerShell (run as Administrator)
- Defender must be installed and registered
- Internet access
- Permissions to write to `%TEMP%` and `%USERPROFILE%\Desktop`

---

## How to Use the Script

1. Open **PowerShell as Administrator**
2. Copy and paste the full script (below) into the console or save it as a `.ps1` file
3. Run the script
4. Wait for it to complete (usually under 1 minute)
5. Locate two files on your desktop:
   - `Defender_ECS_Report_<timestamp>.txt` – contains diagnostics and logs
   - `Defender_ECS_Capture_<timestamp>.etl` – contains network traffic capture

---

## Script

```powershell
# --- Setup Paths and Timestamps ---
$desktopPath = [Environment]::GetFolderPath("Desktop")
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportName = "Defender_ECS_Report_$timestamp.txt"
$reportPath = Join-Path $desktopPath $reportName
$traceName = "Defender_ECS_Capture_$timestamp.etl"
$traceTempPath = Join-Path $env:TEMP $traceName
$traceFinalPath = Join-Path $desktopPath $traceName

# Clear/Create report file
"" | Out-File -FilePath $reportPath -Encoding UTF8

# --- Start Network Capture ---
"Starting network capture..." | Tee-Object -FilePath $reportPath -Append
netsh trace start capture=yes tracefile="$traceTempPath" persistent=no maxsize=100 overwrite=yes | Out-String | Tee-Object -FilePath $reportPath -Append

# --- Locate MpCmdRun.exe in Latest Defender Platform ---
$basePath = "C:\ProgramData\Microsoft\Windows Defender\Platform"
$latestDir = Get-ChildItem -Path $basePath -Directory |
    Where-Object { $_.Name -match '^\d+\.\d+\.\d+\.\d+-\d+$' } |
    Sort-Object Name -Descending |
    Select-Object -First 1

$mpCmdRunPath = Join-Path -Path $latestDir.FullName -ChildPath "MpCmdRun.exe"

"Latest Defender Platform: $($latestDir.Name)" | Tee-Object -FilePath $reportPath -Append

# --- Get ECS Base URL ---
$ecsOutput = & $mpCmdRunPath -DisplayECSConnection
$ecsBaseUrl = ($ecsOutput | Where-Object { $_ -match '^ECS Url:' }) -replace '^ECS Url:\s*', ''

# --- Build Full URL ---
$queryString = '?CampPlatformVersion=6&EngineMinorVersion=1&EngineRing=2&EngineVersion=25060&IsBeta=0&IsEmbedded=0&IsEnterprise=1&IsMsSense=1&IsMsft=0&IsServer=1&IsSeville=1&MoCampBuildRev=1641676800&MoCampVersion=262162&OsBuildMinNumber=2134&OsBuildNumber=22621&OsMajorMinorVersion=655360&PlatformRing=2&SignatureRing=5&Engine_Ring=2'
$finalUrl = "$ecsBaseUrl" + 'MicrosoftWindowsDefenderClient/1.0.0.0' + $queryString

"Final ECS URL: $finalUrl" | Tee-Object -FilePath $reportPath -Append

# --- DNS and Connectivity Tests ---
try {
    $ecsUri = [System.Uri]$finalUrl
    $hostName = $ecsUri.Host

    "DNS Lookup for ${hostName}:" | Tee-Object -FilePath $reportPath -Append
    Resolve-DnsName $hostName -ErrorAction SilentlyContinue | Out-String | Tee-Object -FilePath $reportPath -Append

    "Port 443 Connectivity Test:" | Tee-Object -FilePath $reportPath -Append
    Test-NetConnection -ComputerName $hostName -Port 443 | Out-String | Tee-Object -FilePath $reportPath -Append
} catch {
    "Could not resolve or test connectivity to $hostName" | Tee-Object -FilePath $reportPath -Append
}

# --- Show System Proxy Settings ---
"System Proxy Configuration:" | Tee-Object -FilePath $reportPath -Append
(netsh winhttp show proxy) | Out-String | Tee-Object -FilePath $reportPath -Append

# --- ECS Web Request ---
try {
    $response = Invoke-WebRequest -Uri $finalUrl -UseBasicParsing -ErrorAction Stop

    "Web Request Successful:" | Tee-Object -FilePath $reportPath -Append
    "Status Code: $($response.StatusCode)" | Tee-Object -FilePath $reportPath -Append
    "Response Headers:" | Tee-Object -FilePath $reportPath -Append
    $response.Headers | Out-String | Tee-Object -FilePath $reportPath -Append
} catch {
    "Web Request Failed:" | Tee-Object -FilePath $reportPath -Append
    "Error Message: $($_.Exception.Message)" | Tee-Object -FilePath $reportPath -Append

    if ($_.Exception.InnerException) {
        "Inner Exception: $($_.Exception.InnerException.Message)" | Tee-Object -FilePath $reportPath -Append
    }

    if ($_.Exception -is [System.Net.WebException]) {
        $webEx = $_.Exception
        if ($webEx.Response) {
            $reader = New-Object System.IO.StreamReader($webEx.Response.GetResponseStream())
            $body = $reader.ReadToEnd()
            "Server Response:" | Tee-Object -FilePath $reportPath -Append
            $body | Tee-Object -FilePath $reportPath -Append
        }
    }
}

# --- Stop Network Capture ---
"Stopping network capture..." | Tee-Object -FilePath $reportPath -Append
netsh trace stop | Out-String | Tee-Object -FilePath $reportPath -Append
Start-Sleep -Seconds 2

# --- Move ETL File to Desktop ---
if (Test-Path $traceTempPath) {
    Move-Item -Path $traceTempPath -Destination $traceFinalPath -Force
    "ETL file saved to: $traceFinalPath" | Tee-Object -FilePath $reportPath -Append
} else {
    "Trace file not found in temp location." | Tee-Object -FilePath $reportPath -Append
}

# --- Final Report Location ---
"Diagnostic report saved to: $reportPath" | Tee-Object -FilePath $reportPath -Append

# --- Open ECS URL in Default Browser ---
Start-Process $finalUrl
```

---

## Sample Output

### Desktop Files:

- `Defender_ECS_Report_20250707_114122.txt`
- `Defender_ECS_Capture_20250707_114122.etl`

### ECS Report (Excerpt):

```
Latest Defender Platform: 4.18.25050.5-0
Final ECS URL: https://mdav.us.endpoint.security.microsoft.com/ecs/config/v1/MicrosoftWindowsDefenderClient/1.0.0.0?...
DNS Lookup for mdav.us.endpoint.security.microsoft.com:
...

Port 443 Connectivity Test:
TcpTestSucceeded : True

Web Request Successful:
Status Code: 200
Response Headers:
...
```

---

## Troubleshooting Tips

- **DNS Failure**: Check internal DNS rules or host resolution for the ECS domain.
- **Port Blocked**: Use `Test-NetConnection` output to identify firewall or network issues.
- **Proxy Config**: Ensure the proxy allows outbound HTTPS access to ECS domains.
- **Certificate/Privacy Errors**: The script captures detailed exceptions including SSL/TLS failures.
- **Timeouts**: Check latency or packet loss in the `.etl` capture using Network Monitor or Wireshark.

---

## Limitations

- Script must be run **with administrative privileges**
- `.etl` files require parsing with tools like Microsoft Message Analyzer or Wireshark
- Script does not attempt retries or alternate ECS endpoints

---

## Next Steps

If the script shows failures or abnormal output:

1. Review proxy/firewall configurations for ECS domains
2. Upload the `.etl` file to a secure analysis tool
3. Provide the `.txt` report to Microsoft Support for further diagnosis
4. Refer to ECS documentation for required domains and IP ranges

---

## Related Articles

- `[MDECA: What it checks and what it misses]`
- `[Troubleshooting MDE connectivity issues]`
- `[Understanding ECS traffic flow]`

---

