m = re.search(r"hgt:(\d+)(cm|in)", passw)
if m:
    value = int(m.group(1))
    unit = m.group(2)
    if unit == "cm":
        valid = 150 <= value <= 193 and valid
    elif unit == "in":
        valid = 59 <= value <= 76 and valid
    else:
        valid = False
else:
    valid = False
