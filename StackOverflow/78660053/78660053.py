import random
import time


# === CONFIG ===

_AXE = r"""
  ,  /\  .
 //`-||-'\\
(| -=||=- |)
 \\,-||-.//
  `  ||  '
     ||
     ||
     ||
     ||
     ||
     ()
"""[1:-1]

_BOW = r"""
    (
     \
      )
##-------->
      )
     /
    (
"""[1:-1]

# ...Preferably move above to other script for better management


# === UTILITY ===

def delayed_print(*args, delay=1, **kwargs):
    """Prints with a following delay"""
    print(*args, **kwargs)
    time.sleep(delay)


# === WEAPON CLASS ===

class Weapon:
    """Weapon class that calculates and show the attack result."""

    def __init__(self, name: str, damage: int, roll_check: int, ascii_art: str):
        self.name = name
        self.damage = damage
        self.roll_check = roll_check
        self._ascii_art = ascii_art

    def attack(self, roll_check):
        """Checks if the attack hits and print if hit. Returns damage dealt."""

        if roll_check < self.roll_check:
            delayed_print("Attack missed!")
            return 0

        print(self._ascii_art)
        delayed_print(f"Attack hit!")
        return self.damage + (roll_check - self.roll_check)


WEAPONS = [
    Weapon("Axe", 10, 4, _AXE),
    Weapon("Bow", 5, 2, _BOW),
]


def get_weapon_options():
    """Gets player's weapon choice. Returns the weapon."""

    print("Choose a weapon:")

    for i, weapon in enumerate(WEAPONS):
        print(f"{i + 1}. {weapon.name:<4} - DMG: {weapon.damage:<3} / Roll check: {weapon.roll_check}")

    choice = 0
    while choice not in range(1, len(WEAPONS) + 1):
        try:
            choice = int(input(">> "))
        except ValueError:
            continue

    return WEAPONS[choice - 1]


# === ENTITY CLASS ===

class Entity:
    """Entity class that represents a player or enemy"""

    def __init__(self, name: str, health: int, weapon: Weapon):
        self.name = name
        self.health = health
        self.weapon = weapon

    def attack(self, target: "Entity", roll_check: int):
        """Attacks the target entity."""

        damage = self.weapon.attack(roll_check)
        target.health = max(0, target.health - damage)

        delayed_print(f"{self.name} attacked {target.name} with {damage} damage!")
        delayed_print(f"{target.name} has {target.health} health remaining!")


def main():
    player = Entity("Player", 100, get_weapon_options())
    enemy = Entity("Enemy", 100, random.choice(WEAPONS))

    turn = 1

    while True:
        delayed_print(f"\nTurn {turn}:\nPlayer health: {player.health} / Enemy health: {enemy.health}")

        # player turn
        input(f"Press enter to roll the dice! (Roll check: {player.weapon.roll_check})")
        attack_check = random.randint(1, 6)

        delayed_print(f"You rolled a {attack_check}!")
        player.attack(enemy, attack_check)

        # check if enemy is dead
        if enemy.health <= 0:
            break

        # enemy turn
        delayed_print(f"\nEnemy rolls the dice! (Roll check: {enemy.weapon.roll_check})")
        attack_check = random.randint(1, 6)

        delayed_print(f"Enemy rolled a {attack_check}!")
        enemy.attack(player, attack_check)

        # check if player is dead
        if player.health <= 0:
            break

        input("\nPress enter to continue...\n")

    delayed_print("You died!" if enemy.health > 0 else "You won!")

    input("Press enter to exit...")


if __name__ == '__main__':
    main()
