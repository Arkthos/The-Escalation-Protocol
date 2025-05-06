import json
import os
import platform
from pathlib import Path

def prompt_input(prompt_text, required=True, cast=str, tip=None):
    while True:
        if tip:
            print(f"💡 {tip}")
        user_input = input(f"{prompt_text.strip()} ").strip()
        if not user_input and not required:
            return None
        if prompt_yes_no("Would you like to preview the generated policy before saving?"):
        print("\n📄 Policy Preview:")
        print(json.dumps(policy, indent=2))


            return cast(user_input)
        except ValueError:
            print("❗ Invalid input type. Please try again.")

def prompt_choice(prompt_text, choices, tip=None):
    print(f"{prompt_text}")
    if tip:
        print(f"💡 {tip}")
    for idx, choice in enumerate(choices, start=1):
        print(f"  {idx}. {choice}")
    while True:
        selection = input("Enter the number of your choice: ").strip()
        if selection.isdigit() and 1 <= int(selection) <= len(choices):
            return choices[int(selection) - 1]
        print("❗ Invalid choice. Please enter a number from the list.")

def prompt_multiselect(prompt_text, choices, tip=None):
    print(f"{prompt_text}")
    if tip:
        print(f"💡 {tip}")
    for idx, choice in enumerate(choices, start=1):
        print(f"  {idx}. {choice}")
    print("Enter numbers separated by commas (e.g., 1,3):")
    while True:
        selection = input("Your choices: ").strip().split(",")
        if prompt_yes_no("Would you like to preview the generated policy before saving?"):
        print("\n📄 Policy Preview:")
        print(json.dumps(policy, indent=2))


            result = [choices[int(s.strip()) - 1] for s in selection if s.strip().isdigit()]
            if result:
                return result
        except (ValueError, IndexError):
            pass
        print("❗ Invalid input. Please try again.")

def prompt_yes_no(question, tip=None):
    if tip:
        print(f"💡 {tip}")
    while True:
        ans = input(f"{question} (y/n): ").lower().strip()
        if ans in ['y', 'yes']:
            return True
        elif ans in ['n', 'no']:
            return False
        print("❗ Please answer 'y' or 'n'.")

def create_device_group(group_id, name, device_type, allow_exceptions):
    device_map = {
        "Removable Media": "removable_media_devices",
        "Bluetooth": "bluetooth_devices",
        "Printers": "printer_devices",
        "Storage": "storage_devices"
    }

    group = {
        "id": group_id,
        "name": name,
        "query": {
            "$type": "primaryId",
            "value": device_map[device_type]
        }
    }

    if allow_exceptions:
        vendor_id = prompt_input("Enter allowed Vendor ID (hex, e.g., 0951):", tip="This is the USB vendor identifier.")
        product_ids = input("Enter allowed Product IDs (comma-separated, e.g., 1234,5678): ").split(",")
        group["query"] = {
            "$type": "all",
            "clauses": [
                {"$type": "vendorId", "value": vendor_id},
                {
                    "$type": "any",
                    "clauses": [{"$type": "productId", "value": pid.strip()} for pid in product_ids]
                }
            ]
        }

    return group

def create_rule(rule_id, include_group_id, exclude_group_id, access_types, enforcement):
    entries = []
    for access in access_types:
        entries.append({
            "$type": "removableMedia",
            "id": f"{rule_id}_{access}",
            "enforcement": {"$type": enforcement},
            "access": [access]
        })
        if enforcement == "deny":
            entries.append({
                "$type": "removableMedia",
                "id": f"{rule_id}_{access}_audit",
                "enforcement": {
                    "$type": "auditDeny",
                    "options": ["send_event", "show_notification"]
                },
                "access": [access]
            })
    return {
        "id": rule_id,
        "name": f"Policy for {', '.join(access_types)} access",
        "includeGroups": [include_group_id],
        "excludeGroups": [exclude_group_id],
        "entries": entries
    }

def main():
    print("🔧 Defender for Endpoint Device Control Policy Generator (Enhanced Version)")

    scenario = prompt_choice(
        "Select your deployment scenario:",
        ["Jamf", "Intune"],
        tip="This will guide naming and assumptions about platform delivery."
    )

    device_types = prompt_multiselect(
        "What type of devices do you want to control?",
        ["Removable Media", "Bluetooth", "Printers", "Storage"],
        tip="You can select multiple types."
    )

    access_types = prompt_multiselect(
        "What type of access should be controlled?",
        ["read", "write", "execute"],
        tip="You can select multiple access types."
    )

    enforcement = prompt_choice(
        "What enforcement should apply?",
        ["allow", "deny"],
        tip="'Deny' blocks access; 'Allow' permits it. 'deny' usually comes with audit logging."
    )

    allow_exceptions = prompt_yes_no("Do you want to allow specific exceptions (e.g., based on Vendor/Product IDs)?")

    default_enforcement = prompt_choice(
        "Set the default enforcement for devices not covered by rules:",
        ["allow", "deny"],
        tip="This sets the fallback behavior if no rule matches."
    )

    groups = []
    rules = []

    for idx, dtype in enumerate(device_types, start=1):
        group_all = create_device_group(f"group_all_{idx}", f"All {dtype}", dtype, False)
        group_allowed = create_device_group(f"group_allowed_{idx}", f"Allowed {dtype}", dtype, allow_exceptions)
        rule = create_rule(f"rule_{idx}", group_all["id"], group_allowed["id"], access_types, enforcement)
        groups.extend([group_all, group_allowed])
        rules.append(rule)

    policy = {
        "version": 1,
        "settings": {
            "features": { "removableMedia": { "disable": False } },
            "global": { "defaultEnforcement": default_enforcement }
        },
        "groups": groups,
        "rules": rules
    }

    if prompt_yes_no("Would you like to preview the generated policy before saving?"):
        print("\n📄 Policy Preview:")
        print(json.dumps(policy, indent=2))


        desktop_path = Path.home() / "Desktop" / "device_control_policy.json"
        with open(desktop_path, "w") as f:
            json.dump(policy, f, indent=2)
        print(f"\n✅ Policy saved to: {desktop_path}")
    except Exception as e:
        print("⚠️ Could not save to desktop. Outputting JSON below:")
        print(json.dumps(policy, indent=2))

    print("\n📌 Reminder: Validate the policy using:")
    print("mdatp device-control policy validate --path <path-to-your-json-file>")

if __name__ == "__main__":
    main()
