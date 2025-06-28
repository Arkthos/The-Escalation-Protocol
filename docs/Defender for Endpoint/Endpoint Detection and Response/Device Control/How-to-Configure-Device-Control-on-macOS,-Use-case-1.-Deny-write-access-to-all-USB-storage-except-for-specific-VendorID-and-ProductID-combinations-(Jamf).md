## Summary

This article describes how to configure **Microsoft Defender for Endpoint (MDE) Device Control** on **macOS** to **block write access to all removable media**, while still allowing write access to a specific subset of **Kingston USB drives** based on their **Vendor ID** and **Product ID**. The policy is deployed using **Jamf Pro**.

The guidance includes:

- An overview of how device control works in MDE on macOS  
- Step-by-step instructions for building the custom policy  
- Validation tips before deployment  
- References to official Microsoft documentation  

> ✅ **Use case:** You want to ensure only company-approved USB drives can be written to on managed macOS devices, as part of your data loss prevention (DLP) or endpoint hardening strategy.

---

## Environment

- **Product:** Microsoft Defender for Endpoint (macOS)  
- **OS:** macOS 11+ (Big Sur or later)  
- **MDM:** Jamf Pro  
- **Requirement:** Defender for Endpoint CLI installed  

---

## Background

Microsoft Defender for Endpoint supports **device control** on macOS, allowing administrators to:

- **Block or allow** read/write access to specific types of hardware  
- **Target devices** by attributes such as `vendorId`, `productId`, and device class  
- Use **JSON-based policy** delivered via **MDM configuration profiles**  

On macOS, device control policies must be authored manually in JSON and validated locally using the Defender CLI before deployment through Jamf.

---

## Problem

You need to:

1. **Block write access** to all removable media (e.g., USB flash drives)  
2. **Allow write access** to a select group of **Kingston USB drives**, identified by a **Vendor ID** (`0951`) and multiple **Product IDs**  

This ensures users can only write to **pre-approved USB drives**, reducing data exfiltration risk.

---

## Solution

### 🔹 Step 1: Define Device Groups

We will define:

- A group that matches **all removable media devices**  
- A second group that includes only the **approved Kingston USB drives**

```json
"groups": [
  {
    "id": "group1",
    "name": "All Removable Media Devices",
    "query": {
      "$type": "primaryId",
      "value": "removable_media_devices"
    }
  },
  {
    "id": "group2",
    "name": "Allowed Kingston USBs",
    "query": {
      "$type": "all",
      "clauses": [
        { "$type": "vendorId", "value": "0951" },
        {
          "$type": "any",
          "clauses": [
            { "$type": "productId", "value": "1234" },
            { "$type": "productId", "value": "5678" },
            { "$type": "productId", "value": "9012" }
          ]
        }
      ]
    }
  }
]
```

#### 📘 Explanation

- `0951` is the **Vendor ID for Kingston**  
- The `any` clause matches **any of the listed Product IDs**, allowing flexibility if multiple Kingston USB models are in use  
- These device groups act as the **foundation** for rules later in the policy

---

### 🔹 Step 2: Define Write Access Rule

Create a rule that:

- **Includes all removable media**  
- **Excludes the allowed Kingston USB group**  
- **Denies write access**  
- Optionally **audits and notifies** on denied attempts

```json
"rules": [
  {
    "id": "rule1",
    "name": "Block Write Access Except for Allowed Kingston Devices",
    "includeGroups": [ "group1" ],
    "excludeGroups": [ "group2" ],
    "entries": [
      {
        "$type": "removableMedia",
        "id": "entry1",
        "enforcement": { "$type": "deny" },
        "access": [ "write" ]
      },
      {
        "$type": "removableMedia",
        "id": "entry2",
        "enforcement": {
          "$type": "auditDeny",
          "options": [ "send_event", "show_notification" ]
        },
        "access": [ "write" ]
      }
    ]
  }
]
```

#### 📘 Explanation

- `includeGroups` targets **all USB drives**  
- `excludeGroups` removes **only the approved Kingston USBs**  
- `deny` blocks write access for non-approved drives  
- `auditDeny` triggers event logging and user notifications  

---

### 🔹 Step 3: Validate the Policy Locally

Use the Defender CLI to validate your JSON before deployment:

```bash
mdatp device-control policy validate --path /path/to/your-policy.json
```

#### 📘 Explanation

- Ensures the JSON is syntactically correct and matches Defender’s schema  
- Prevents deployment failures due to malformed profiles

---

### 🔹 Step 4: Deploy via Jamf Pro

Once validated:

1. Wrap the JSON in a **Jamf custom configuration profile**  
2. Use the **preference domain**: `com.microsoft.wdav`  
3. Deploy the profile to scoped macOS devices  

> 💡 For help creating configuration profiles in Jamf, refer to the [Jamf Custom Profiles Guide](https://docs.jamf.com/).

---

## ✅ Best Practices

- Always **test on a non-production device**  
- **Keep your JSON policy files in version control**  
- Maintain an **inventory of approved Vendor/Product IDs**  
- **Educate users** on new restrictions to avoid support tickets  

---

## 📚 References

- [📘 Device Control on macOS – Microsoft Docs](https://learn.microsoft.com/en-us/defender-endpoint/mac-device-control-jamf)  
- [💾 Microsoft Defender GitHub – Sample JSON Files](https://github.com/MicrosoftDocs/microsoft-365-docs)  
- [🛠️ Jamf Pro: Custom Configuration Profiles](https://docs.jamf.com/)  

## Additional tips:

You can build simple policies based on your use case using the [Policy Builder](https://github.com/Arkthos/The-Escalation-Protocol/wiki/Using-the-device-control-policy-sample-builder)

---

**Author:** Arkthos
