import re
import os

file_path = r"c:\Users\one09\Desktop\wms\orders\templates\orders\order_list_final.html"

def fix_file():
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("--- Initial Check ---")
    # Check for split tag
    pattern_split = r'({% if order\.order_status\s*==\s*[\'"]SHIPPED[\'"])\s*\n\s*(%\}disabled{% endif %})'
    split_matches = re.findall(pattern_split, content)
    print(f"Split tags found: {len(split_matches)}")
    
    # Check for double quote tag (single line but double quotes)
    pattern_dq = r'{% if order\.order_status\s*==\s*"SHIPPED"\s*%}disabled{% endif %}'
    dq_matches = re.findall(pattern_dq, content)
    print(f"Double quote tags found: {len(dq_matches)}")

    # Check for correct message
    msg_correct = "접수취소 하시겠습니까?" in content
    print(f"Confirmation message correct? {msg_correct}")

    new_content = content

    # 1. FIX SPLIT TAG
    if split_matches:
        print("Fixing split tags...")
        new_content = re.sub(pattern_split, r"{% if order.order_status == 'SHIPPED' %}disabled{% endif %}", new_content)
    
    # 2. NORMALIZE DOUBLE QUOTES
    if dq_matches:
        print("Normalizing double quotes...")
        new_content = re.sub(pattern_dq, r"{% if order.order_status == 'SHIPPED' %}disabled{% endif %}", new_content)

    # 3. ENSURE MESSAGE IS CORRECT
    if not msg_correct:
        print("Fixing confirmation message...")
        old_msg = "이 오류 항목을 삭제하시겠습니까?"
        if old_msg in new_content:
             new_content = new_content.replace(old_msg, "접수취소 하시겠습니까?")
        else:
             print("WARNING: Could not find old confirmation message to replace.")

    # Write back if changed
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("File updated successfully.")
    else:
        print("No changes needed (or logic failed to match).")

    # Final Verification
    if "접수취소 하시겠습니까?" in new_content:
        print("FINAL CHECK: Message is correct.")
    else:
        print("FINAL CHECK: Message is WRONG.")

if __name__ == "__main__":
    fix_file()
