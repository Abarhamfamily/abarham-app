import re

file_path = "bot.py"

# Read the entire file
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the line numbers for the function get_vehicle_choice_and_save
# We'll do a simple search for the function definition and then find the deposit calculation lines.
# We know the deposit calculation lines are after the participant creation and before the keyboard.
# We'll look for the pattern:
#            deposit_amount = calculate_deposit(trip.price)
#            full_amount = calculate_full_amount(trip.price, 0)
# and replace with the effective price version.

# We'll join the lines into a string for easier regex, but we need to be careful with multiline.
content = ''.join(lines)

# Pattern to find the two lines we want to replace
pattern = r'(\s+deposit_amount = calculate_deposit\(trip\.price\)\n\s+full_amount = calculate_full_amount\(trip\.price, 0\))'

# Replacement string
replacement = '''            effective_price = get_effective_trip_price(trip, participant)
            deposit_amount = calculate_deposit(effective_price)
            full_amount = calculate_full_amount(effective_price, 0)'''

# Perform the replacement
new_content = re.sub(pattern, replacement, content)

# Write back
with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(new_content)

print("Replacement done.")