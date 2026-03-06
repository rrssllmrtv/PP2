#1
import re

s = input()
pat = r"ab*"

if re.fullmatch(pat, s): print("Match")
else: print("No match")

#2
import re

s = input()
pat = r"ab{2,3}"

if re.fullmatch(pat, s): print("Match")
else: print("No match")

#3
import re

s = input()
pat = r"[a-z]+_[a-z]+"

if re.fullmatch(pat, s): print("Match")
else: print("No match")

#4
import re

s = input()
pat = r"[A-Z][a-z]+"

if re.fullmatch(pat, s): print("Match")
else: print("No match")

#5
import re

s = input()
pat = r"a.*b$"

if re.fullmatch(pat, s): print("Match")
else: print("No match")

#6
import re

s = input()
res = re.sub(r"[ ,\.]", ":", s)
print(res)

#7
import re

s = input()

parts = s.split("_")
camel = parts[0] + "".join(word.capitalize() for word in parts[1:])

print(camel)

#8
import re

s = input()
res = re.split(r"(?=[A-Z])", s)
print(res)

#9
import re

s = input()
res = re.sub(r"(?<!^)([A-Z])", r" \1", s)
print(res)

#10
import re

s = input()
res = re.sub(r"(?<!^)([A-Z])", r"_\1", s).lower()
print(res)