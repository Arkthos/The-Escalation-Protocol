
# How to Manually Test Microsoft Defender’s ECS Networking Component

## Summary

Microsoft Defender for Endpoint (MDE) includes an ECS (Endpoint Cloud Service) component responsible for coordinating cloud-based threat intelligence and updates. While most ECS functionality is validated by the Client Analyzer tool, the **networking portion is not tested** by it. This article explains the behavior and provides a script to manually verify ECS connectivity and DNS resolution.

---

## Details

**Environment:**
- Microsoft Defender for Endpoint  
- Windows 10/11, Server 2016-2022  
- ECS functionality enabled  

**Issue:**
ECS connectivity issues may arise, but the **Client Analyzer** tool does **not** currently test the **network layer** or the ability to reach ECS endpoints over HTTPS.

**Clarification:**
The ECS module uses specific telemetry URLs and network routes that may not follow the standard update or telemetry paths. Manual validation is often required, especially in environments with custom proxies, DPI/SSL inspection, or strict outbound firewall rules.

---

## Solution: Manual ECS Network Test Script

The following PowerShell script performs:

- Network trace capture  
- ECS URL detection  
- DNS resolution  
- Port 443 connectivity test  
- Proxy configuration readout  
- ECS endpoint web request

> **Note:** Run this in an **elevated PowerShell session**. The script will create a `.txt` report and `.etl` network trace file on the user's Desktop.

<details>
<summary><strong>Click to expand the full PowerShell script</strong></summary>

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
</details>

---

## Output

- **ETL File:** Captures ECS network traffic  
- **Report File:** Includes:
  - Platform version used
  - ECS base and full URLs
  - DNS resolution results
  - Port 443 connectivity
  - Proxy config
  - ECS web request result

---

## Additional Notes

- If the `Invoke-WebRequest` fails, investigate proxy settings, DNS filtering, or outbound HTTPS rules.
- ECS uses `MicrosoftWindowsDefenderClient` URLs that are **not used for AV updates**.

---

## Applies To

- Microsoft Defender for Endpoint  
- Microsoft Defender AV Platform versions 4.18.x and newer
