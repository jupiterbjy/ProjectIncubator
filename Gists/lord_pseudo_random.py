"""
Pseudo Random Picker from CSV input

Usage:
```
Choices (CSV) >>
Saint Pseudorandom once said... "Mah boy! You musn't hesitate..."

Choices (CSV) >> Nanasaki Ai, Komeiji Koishi, Sorasaki Hina
Saint Pseudorandom once said... "Tho shall be Sorasaki Hina"

...
```

:Author: jupiterbjy@gmail.com
"""

import random


YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"


while True:
    raw_input = input(f"{YELLOW}Choices (CSV) >> \33[0m").strip()
    
    # if empty don't bother
    if not raw_input:
        print(f"{GREEN}\33[3mSaint Pseudorandom once said... \"Mah boy! You musn't hesitate...\"\n")
        continue
    
    raw_split = [part.strip() for part in raw_input.split(",")]
    
    choice = raw_split[random.randint(0, len(raw_split) - 1)]
    
    # 0: reset / 3: italic / 4: underline / 5: slow blink
    print(f"{GREEN}\33[3mSaint Pseudorandom once said... \"Tho shall be {RED}\33[4m{choice}\33[0;3m{GREEN}\"\n")
