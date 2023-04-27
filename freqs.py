import re
chars = dict()

chars_total = 0
with open("./input.txt", "r") as fh:
    lines = fh.readlines()
    for line in lines:
        str = re.sub(r'[^a-z]', '', line.lower())
        chars_total = chars_total + len(str)
        for ch in str:
            freq = chars.get(ch, 0)
            chars[ch] = freq + 1

print(chars)
print(chars_total)