import re

file_path = "bot.py"

# Read original content
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern to find the lines we want to replace
# We want to replace:
#            context.user_data[\"payment_participant_id\"] = new_participant.id
#
#            deposit_amount = calculate_deposit(trip.price)
#            full_amount = calculate_full_amount(trip.price, 0)
#
# With:
#            context.user_data[\"payment_participant_id\"] = new_participant.id
#
#            effective_price = get_effective_trip_price(trip, participant)
#            deposit_amount = calculate_deposit(effective_price)
#            full_amount = calculate_full_amount(effective_price, 0)
#
# Note: there is a blank line between the context assignment and the deposit calculation.

pattern = r'(context\.user_data\\[\"payment_participant_id\"\\] = new_participant\.id\n)\n\n(\s+deposit_amount = calculate_deposit\(trip\.price\)\n\s+full_amount = calculate_fullamount\(trip\.price, 0\))'
# Note: I see a typo in the pattern: "calculate_fullamount" missing underscore. Let's fix.

# Let's rewrite the pattern correctly.

pattern = r'(context\.user_data\\[\"payment_participant_id\"\\] = new_participant\.id\n)\n\n(\s+deposit_amount = calculate_deposit\(trip\.price\)\n\s+full_amount = calculate_full_amount\(trip\.price, 0\))'

replacement = r'\1\n\n            effective_price = get_effective_triprip(trip, participant)\n            deposit_amount = calculate_deposit(effective_price)\n            full_amount = calculate_full_amount(effective_price, 0)'

if re.search(pattern, content):
    new_content = re.sub(pattern, replacement, content)
    with open(file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    print("SUCCESS: Replacement applied with context.")
else:
    print("WARNING: Pattern not matched. Trying alternative.")
    # Alternative: match the two calculation lines and the preceding context line and blank line?
    # Let's just replace the two calculation lines and ensure we insert the effective_price line before them.
    pattern2 = r'(\s+deposit_amount = calculate_deposit\(trip\.price\)\n\s+full_amount = calculate_full_amount\(trip\.price, 0\))'
    replacement2 = '''            effective_price = get_effective_trip_price(trip, participant)
            deposit_amount = calculate_deposit(effective_price)
            full_amount = calculate_full_amount(effective_price, 0)'''
    if re.search(pattern2, content):
        new_content = re.sub(pattern2, replacement2, content)
        with open(file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        print("SUCCESS: Replaced calculation lines only.")
    else:
        print("ERROR: Could not find the calculation lines.")