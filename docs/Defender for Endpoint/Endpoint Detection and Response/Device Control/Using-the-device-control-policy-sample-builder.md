This interactive Python script helps you **build basic examples** of Microsoft Defender for Endpoint (MDE) **device control policies**. It guides you through selecting common device types, access rules, and exception conditions — and outputs a valid JSON policy structure that can be deployed via **Jamf** or **Intune**.

> ⚠️ **IMPORTANT:**  
> This tool is intended for **illustration and prototyping purposes only**. It is **not** a production-ready policy generator. Use it to explore and understand the JSON structure of device control policies — not as a replacement for manual policy design and validation.

---

## ✨ Features

- Supports both **Jamf** and **Intune** deployment scenarios
- Interactive prompts for:
  - Device types (USB, Bluetooth, Printers, Storage)
  - Access control types (read, write, execute)
  - Enforcement actions (`allow`, `deny`, `auditDeny`)
  - Vendor/Product ID exceptions
  - Additional fields like `serialNumber` and `interfaceClass`
- Generates a complete JSON policy with:
  - `groups`
  - `rules`
  - `settings`
- Saves the output to your **Desktop** or prints it to the screen
- Offers a **preview** of the policy before saving

---

## 🧰 Requirements

- Python 3.6+
- macOS, Linux, or Windows with write access to the desktop

---

## 🚀 Usage

1. Download the script:  
   [`device_control_policy_generator.py`](https://github.com/Arkthos/The-Escalation-Protocol/blob/main/Scripts/device_control_policy_generator.py)

2. Run it in a terminal:
   ```bash
   python3 device_control_policy_generator.py
   ```

3. Answer the interactive prompts:
   - Choose one or more device types to control
   - Specify access types (write, read, execute)
   - Define enforcement actions and exceptions
   - Optionally preview the final JSON before saving

4. The script will attempt to save the generated policy as:
   ```
   ~/Desktop/device_control_policy.json
   ```

---

## 🧪 Validation

Once generated, validate the policy on a macOS device with Microsoft Defender CLI:
```bash
mdatp device-control policy validate --path ~/Desktop/device_control_policy.json
```

---

## 🔒 Limitations

- This tool **does not validate policies against the full schema** — please test carefully.
- Generated policies are **basic templates** — they **may need additional customization** before real-world deployment.
- Only a subset of device identification methods are supported (e.g., no `friendlyName`, `interfaceSubClass`, etc.).

---

## 👷 Disclaimer

This tool is provided as-is for **educational and advisory use only**.  
By using it, you acknowledge:
- You are responsible for testing and validating the output.
- Microsoft support does **not** cover the use of custom policy generators.
- For production scenarios, consult your CSAM or official Microsoft documentation.

---

## 📚 References

- [Microsoft Defender for Endpoint – Device Control on macOS](https://learn.microsoft.com/microsoft-365/security/defender-endpoint/device-control-macos)
- [Microsoft GitHub – JSON Schema & Sample Policies](https://github.com/microsoft/mdatp-devicecontrol)

---

## 📬 Feedback

Suggestions or bug reports? Feel free to share ideas for improvement with your engineering team or automation lead.
