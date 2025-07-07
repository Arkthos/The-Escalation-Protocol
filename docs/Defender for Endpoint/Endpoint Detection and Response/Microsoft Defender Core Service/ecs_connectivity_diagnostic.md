# Diagnosing Microsoft Defender Endpoint ECS Connectivity Issues

## Summary

This article provides a PowerShell-based diagnostic approach to validate and capture telemetry for **Microsoft Defender for Endpoint's ECS (Endpoint Configuration Service)** connectivity. It includes a script that collects connection test results, logs, and a network capture to assist with troubleshooting ECS reachability issues, which are **not currently covered by MDE Client Analyzer (MDECA)**.

---

## What is ECS?

**ECS (Endpoint Configuration Service)** is a Microsoft cloud service used by Windows Defender and Microsoft Defender for Endpoint (MDE) clients to retrieve configuration data such as feature flags, diagnostic settings, and platform behavior instructions. ECS URLs are dynamically assigned and can vary based on region, tenant, or client configuration.

> [ECS documentation](https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-core-service-overview)


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

## What the Script Does

| Step | Description                                                               |
| ---- | ------------------------------------------------------------------------- |
| 1    | Starts a network capture using `netsh trace`                              |
| 2    | Locates the latest `MpCmdRun.exe` under Defender's `Platform` directory   |
| 3    | Runs `MpCmdRun.exe -DisplayECSConnection` to get the current ECS base URL |
| 4    | Constructs the full ECS configuration URL with required query parameters  |
| 5    | Performs a DNS resolution and port 443 check                              |
| 6    | Displays and logs current system proxy configuration                      |
| 7    | Sends an HTTPS request to the ECS URL, logging headers and response       |
| 8    | Stops the network capture and moves the `.etl` to the desktop             |
| 9    | Opens the ECS URL in the default web browser                              |
| 10   | Writes a comprehensive log file to the desktop                            |

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

## Version History

| Version | Date       | Author       | Notes                      |
| ------- | ---------- | ------------ | -------------------------- |
| 1.0     | 2025-07-07 | Support Team | Initial script and article |

---

