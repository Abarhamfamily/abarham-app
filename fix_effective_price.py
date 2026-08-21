import re

file_path = "bot.py"

# Read original content
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Correct block replacement for the deposit and full amount calculation
# We need to replace the two lines after the participant creation and before the keyboard creation.
# We'll look for the pattern:
#            deposit_amount = calculate_deposit(trip.price)
#            full_amount = calculate_full_amount(trip.price, 0)
# And replace with:
#            effective_price = get_effective_trip_price(trip, participant)
#            deposit_amount = calculate_deposit(effective_price)
#            full_amount = calculate_full_amount(effective_price, 0)

pattern = r'(\s+deposit_amount = calculate_deposit\(trip\.price\)\n\s+full_amount = calculate_full_amount\(trip\.price, 0\))'
replacement = '''            effective_price = get_effective_trip_price(trip, participant)
            deposit_amount = calculate_deposit(effective_price)
            full_amount = calculate_full_amount(effective_price, 0)'''

if re.search(pattern, content):
    new_content = re.sub(pattern, replacement, content)
    with open(file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    print("SUCCESS: Replacement applied for deposit/full amount calculation.")
else:
    print("WARNING: Pattern not matched for deposit/full amount calculation.")
    # Try a more flexible pattern
    pattern2 = r'deposit_amount = calculate_deposit\(trip\.price\)\s*\n\s*full_amount = calculate_full_amount\(trip\.price, 0\)'
    if re.search(pattern2, content):
        new_content = re.sub(pattern2, replacement, content)
        with open(file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        print("SUCCESS: Replacement applied via flexible pattern.")
    else:
        print("ERROR: Could not find deposit/full amount calculation lines.")