# === CITROGANG COMBAT ENGINE ===

import time
import random

WEAPONS = {
    "bat":       {"inflicts": "STAGGER",   "exploits": False, "type": "concentrated"},
    "chain":     {"inflicts": "RESTRAIN",  "exploits": False, "type": "splash"},
    "belt":      {"inflicts": "EXPOSE",    "exploits": False, "type": "concentrated"},
    "knuckles":  {"inflicts": "BREAK",     "exploits": False, "type": "splash"},
    "slingshot": {"inflicts": "DISORIENT", "exploits": False, "type": "concentrated"},
    "brick":     {"inflicts": None,        "exploits": True,  "type": "splash"},
}

CONDITION_DESCRIPTIONS = {
    "STAGGER":   "off balance, vulnerable to follow-up",
    "RESTRAIN":  "movement locked, easier to hit",
    "EXPOSE":    "defence lowered",
    "BREAK":     "armour or guard compromised",
    "DISORIENT": "accuracy reduced, confused",
}

WEAPON_DAMAGE = {
    "bat":       20,
    "chain":     20,
    "belt":      15,
    "knuckles":  15,
    "slingshot": 10,
    "brick":     10,
}

CLASS_WEAPONS = {
    "heavy":    ["bat", "chain"],
    "medium":   ["belt", "knuckles"],
    "catalyst": ["belt", "knuckles"],
    "light":    ["slingshot", "brick"],
}

CLASS_CREDIT_CAP = {
    "heavy":    3,
    "medium":   4,
    "catalyst": 3,
    "light":    5,
}

CLASS_HP = {
    "heavy":    100,
    "medium":   75,
    "catalyst": 80,
    "light":    60,
}

PERSONALITY_MULTIPLIERS = {
    ("reckless",   "reckless"):   2.2,
    ("stubborn",   "stubborn"):   1.2,
    ("calculated", "calculated"): 1.3,
    ("loyal",      "loyal"):      1.5,
    ("charming",   "charming"):   1.1,
    ("volatile",   "volatile"):   2.3,
    ("reckless",   "stubborn"):   1.8,
    ("calculated", "stubborn"):   1.4,
    ("loyal",      "stubborn"):   1.3,
    ("charming",   "stubborn"):   0.9,
    ("stubborn",   "volatile"):   1.7,
    ("calculated", "reckless"):   0.8,
    ("loyal",      "reckless"):   0.8,
    ("charming",   "reckless"):   1.5,
    ("reckless",   "volatile"):   2.1,
    ("calculated", "loyal"):      1.6,
    ("charming",   "calculated"): 1.4,
    ("calculated", "volatile"):   2.0,
    ("charming",   "loyal"):      1.4,
    ("loyal",      "volatile"):   0.7,
    ("charming",   "volatile"):   1.6,
}

CREDIT_CAP   = 15
CREDIT_START = 10


# === ROSTER ===

PLAYER_ROSTER = [
    {
        "name":          "Citro",
        "class":         "catalyst",
        "hp":            80,
        "max_hp":        80,
        "personalities": ["determined", "loyal"],
        "is_citro":      True,
    },
    {
        "name":          "Kaban",
        "class":         "heavy",
        "hp":            100,
        "max_hp":        100,
        "personalities": ["stubborn", "reckless"],
        "is_citro":      False,
    },
    {
        "name":          "Vovk",
        "class":         "medium",
        "hp":            75,
        "max_hp":        75,
        "personalities": ["charming", "calculated"],
        "is_citro":      False,
    },
    {
        "name":          "Mykola",
        "class":         "heavy",
        "hp":            100,
        "max_hp":        100,
        "personalities": ["stubborn", "loyal"],
        "is_citro":      False,
    },
    {
        "name":          "Daryna",
        "class":         "light",
        "hp":            60,
        "max_hp":        60,
        "personalities": ["charming", "volatile"],
        "is_citro":      False,
    },
    {
        "name":          "Bohdan",
        "class":         "medium",
        "hp":            75,
        "max_hp":        75,
        "personalities": ["calculated", "stubborn"],
        "is_citro":      False,
    },
    {
        "name":          "Oksana",
        "class":         "light",
        "hp":            60,
        "max_hp":        60,
        "personalities": ["reckless", "volatile"],
        "is_citro":      False,
    },
    {
        "name":          "Pavlo",
        "class":         "heavy",
        "hp":            100,
        "max_hp":        100,
        "personalities": ["reckless", "charming"],
        "is_citro":      False,
    },
]

ENEMY_ROSTER = [
    {
        "name":          "Razor",
        "class":         "heavy",
        "hp":            100,
        "max_hp":        100,
        "personalities": ["volatile", "stubborn"],
    },
    {
        "name":          "Brick",
        "class":         "heavy",
        "hp":            100,
        "max_hp":        100,
        "personalities": ["reckless", "volatile"],
    },
    {
        "name":          "Scar",
        "class":         "medium",
        "hp":            75,
        "max_hp":        75,
        "personalities": ["calculated", "charming"],
    },
    {
        "name":          "Knuckles",
        "class":         "medium",
        "hp":            75,
        "max_hp":        75,
        "personalities": ["stubborn", "loyal"],
    },
    {
        "name":          "Dart",
        "class":         "light",
        "hp":            60,
        "max_hp":        60,
        "personalities": ["reckless", "charming"],
    },
    {
        "name":          "Ghost",
        "class":         "light",
        "hp":            60,
        "max_hp":        60,
        "personalities": ["calculated", "volatile"],
    },
    {
        "name":          "Tank",
        "class":         "heavy",
        "hp":            100,
        "max_hp":        100,
        "personalities": ["stubborn", "stubborn"],
    },
    {
        "name":          "Viper",
        "class":         "medium",
        "hp":            75,
        "max_hp":        75,
        "personalities": ["volatile", "charming"],
    },
]


# === HELPER FUNCTIONS ===

def get_personality_multiplier(traits_a, traits_b):
    best = 1.0
    for t1 in traits_a:
        for t2 in traits_b:
            key   = tuple(sorted([t1, t2]))
            value = PERSONALITY_MULTIPLIERS.get(key, 1.0)
            if value > best:
                best = value
    return best


def calculate_citro_multiplier(credits):
    base    = 1.0 + (credits * 0.25)
    penalty = max(0, credits - 3) * 0.1
    return round(base - penalty, 2)


def describe_condition(condition):
    return CONDITION_DESCRIPTIONS.get(condition, "unknown condition")


def pause():
    time.sleep(3)


def apply_damage(target, damage, targets, splash):
    if splash:
        alive_others = [t for t in targets
                        if t["hp"] > 0 and t["name"] != target["name"]]
        primary_dmg  = damage // 2
        other_dmg    = (damage // 2) // len(alive_others) if alive_others else 0

        target["hp"] = max(0, target["hp"] - primary_dmg)
        print(f"    {target['name']}: -{primary_dmg} HP  (remaining: {target['hp']})")

        for t in alive_others:
            if other_dmg > 0:
                t["hp"] = max(0, t["hp"] - other_dmg)
                print(f"    {t['name']}: -{other_dmg} HP  (remaining: {t['hp']})")
    else:
        target["hp"] = max(0, target["hp"] - damage)
        print(f"    {target['name']}: -{damage} HP  (remaining: {target['hp']})")


def print_separator(thin=False):
    print("\n" + ("-" * 40 if thin else "=" * 50))


def print_status(squad, enemies, player_credits, enemy_credits):
    print_separator()
    print(f"  YOUR CREDITS : {player_credits}/{CREDIT_CAP}")
    print(f"  ENEMY CREDITS: {enemy_credits}/{CREDIT_CAP}")

    print("\n  YOUR SQUAD:")
    for i, c in enumerate(squad):
        if c["hp"] <= 0:
            print(f"  [{i+1}] {c['name']:12} DEFEATED")
        else:
            action     = c.get("queued_action")
            action_str = f" — [{action['action_type'].upper()}]" if action else ""
            cap        = CLASS_CREDIT_CAP[c["class"]]
            print(f"  [{i+1}] {c['name']:12} HP: {c['hp']:3}/{c['max_hp']:3}"
                  f"  {c['class'].upper():8}  WPN: {c['weapon']:10}"
                  f"  CAP: {cap}{action_str}")

    print("\n  ENEMIES:")
    for i, e in enumerate(enemies):
        if e["hp"] <= 0:
            print(f"  [{i+1}] {e['name']:12} DEFEATED")
        else:
            conditions = e.get("conditions", [])
            cond_str   = f"  [{', '.join(conditions)}]" if conditions else ""
            print(f"  [{i+1}] {e['name']:12} HP: {e['hp']:3}/{e['max_hp']:3}"
                  f"  {e['class'].upper():8}  WPN: {e['weapon']:10}{cond_str}")
    print_separator()


def pick_from_list(prompt, options, allow_back=True):
    print(f"\n{prompt}")
    for i, opt in enumerate(options):
        print(f"  [{i+1}] {opt}")
    if allow_back:
        print("  [0] Back")
    while True:
        raw = input("> ").strip()
        if raw == "0" and allow_back:
            return -1
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx
        print("  Invalid choice.")


# === SQUAD SELECTION ===

def squad_selection():
    """
    Player selects 4 characters from the roster one by one.
    For each character they also assign a weapon.
    Selection order = execution order.
    Returns a fully configured squad of 4.
    """
    import copy

    print("\n" + "#" * 50)
    print("  SQUAD SELECTION")
    print("#" * 50)
    print("  Select 4 characters in execution order (1 acts first, 4 acts last).")
    print("  Citro must be in slot 4 if you want to catalyse effectively.\n")

    available = list(range(len(PLAYER_ROSTER)))
    squad     = []

    while len(squad) < 4:
        slot = len(squad) + 1
        print(f"\n  --- Slot {slot} ---")
        print("  Available characters:")

        for i in available:
            c   = PLAYER_ROSTER[i]
            cap = CLASS_CREDIT_CAP[c["class"]]
            print(f"  [{i+1}] {c['name']:12} {c['class'].upper():8}"
                  f"  Traits: {', '.join(c['personalities'])}"
                  f"  Credit cap: {cap}")

        while True:
            raw = input("> ").strip()
            if raw.isdigit():
                idx = int(raw) - 1
                if idx in available:
                    break
            print("  Invalid choice.")

        chosen  = copy.deepcopy(PLAYER_ROSTER[idx])
        available.remove(idx)

        # Weapon selection
        weapons = CLASS_WEAPONS[chosen["class"]]
        print(f"\n  Assign weapon to {chosen['name']}:")
        for i, w in enumerate(weapons):
            wdata = WEAPONS[w]
            print(f"  [{i+1}] {w:12}"
                  f"  inflicts: {wdata['inflicts'] or 'EXPLOIT':10}"
                  f"  type: {wdata['type']}")

        while True:
            raw = input("> ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(weapons):
                chosen["weapon"] = weapons[int(raw) - 1]
                break
            print("  Invalid choice.")

        chosen["queued_action"] = None
        chosen["conditions"]    = []
        squad.append(chosen)

        print(f"  -> Slot {slot}: {chosen['name']} with {chosen['weapon']}")

    print("\n  Final squad:")
    for i, c in enumerate(squad):
        print(f"  [{i+1}] {c['name']:12} {c['class'].upper():8}  WPN: {c['weapon']}")

    input("\n  Press Enter to start combat...")
    return squad


def build_enemy_squad():
    """
    Randomly selects 4 enemies from the roster and assigns weapons.
    """
    import copy

    selected = random.sample(ENEMY_ROSTER, 4)
    enemies  = []

    for e in selected:
        enemy          = copy.deepcopy(e)
        weapons        = CLASS_WEAPONS[enemy["class"]]
        enemy["weapon"]     = random.choice(weapons)
        enemy["conditions"] = []
        enemies.append(enemy)

    return enemies


# === TURN BUILDER — PLAYER ===

def build_player_turn(squad, enemies, total_credits):
    credits_remaining = total_credits

    for c in squad:
        c["queued_action"] = None

    while True:
        print_status(squad, enemies, credits_remaining, "?")

        print("  ACTIONS:")
        print("  [1-4] Select squad member")
        print("  [C]   Commit turn")
        print("  [R]   Reset all actions")

        cmd = input("> ").strip().lower()

        if cmd == "c":
            locked = [c for c in squad if c.get("queued_action") and c["hp"] > 0]
            if not locked:
                print("  No actions queued.")
                continue

            citro_action = next(
                (c for c in squad if c.get("queued_action")
                 and c["queued_action"]["action_type"] == "catalyse"),
                None
            )
            if citro_action:
                queue_order = [c for c in squad
                               if c.get("queued_action") and c["hp"] > 0]
                if queue_order[-1]["name"] != citro_action["name"]:
                    print("\n  !! WARNING: Citro is catalysing but is not last"
                          " in execution order. Commit anyway? [Y/N]")
                    if input("> ").strip().lower() != "y":
                        continue

            print(f"\n  Committing {len(locked)} action(s).")
            break

        if cmd == "r":
            for c in squad:
                c["queued_action"] = None
            credits_remaining = total_credits
            print("  Actions reset.")
            continue

        if cmd.isdigit() and 1 <= int(cmd) <= len(squad):
            idx       = int(cmd) - 1
            character = squad[idx]

            if character["hp"] <= 0:
                print(f"  {character['name']} is defeated.")
                continue

            if character.get("queued_action"):
                print(f"  {character['name']} already has an action. Reset to change.")
                continue

            assign_action(character, enemies, credits_remaining)

            credits_remaining = total_credits - sum(
                c["queued_action"]["credits"]
                for c in squad if c.get("queued_action")
            )
        else:
            print("  Invalid input.")

    action_queue = [
        c["queued_action"]
        for c in squad
        if c.get("queued_action") and c["hp"] > 0
    ]

    spent    = sum(a["credits"] for a in action_queue)
    leftover = total_credits - spent
    new_pool = min(leftover + CREDIT_START, CREDIT_CAP)
    if leftover > 0:
        print(f"\n  {leftover} credit(s) carried over. Next pool: {new_pool}/{CREDIT_CAP}")

    return action_queue, new_pool


def assign_action(character, enemies, credits_remaining):
    print(f"\n  {character['name'].upper()} — {character['class'].upper()}"
          f"  WPN: {character['weapon']}  CAP: {CLASS_CREDIT_CAP[character['class']]}")

    options = ["Attack"]
    if character.get("is_citro") or character["class"] == "catalyst":
        options.append("Catalyse")

    choice = pick_from_list("Action:", options)
    if choice == -1:
        return

    action_type = options[choice].lower()

    target = None
    if action_type == "attack":
        alive_enemies = [e for e in enemies if e["hp"] > 0]
        if not alive_enemies:
            print("  No enemies to target.")
            return
        target_names = [f"{e['name']} (HP: {e['hp']}, WPN: {e['weapon']})"
                        for e in alive_enemies]
        t_idx = pick_from_list("Target:", target_names)
        if t_idx == -1:
            return
        target = alive_enemies[t_idx]["name"]

    if credits_remaining <= 0:
        print("  No credits remaining.")
        return

    char_cap   = CLASS_CREDIT_CAP[character["class"]]
    max_spend  = min(credits_remaining, char_cap)

    print(f"\n  Credits available: {credits_remaining}  |  Class cap: {char_cap}"
          f"  |  Max spendable: {max_spend}")
    print(f"  Spend how many? (1-{max_spend})")

    while True:
        raw = input("> ").strip()
        if raw.isdigit() and 1 <= int(raw) <= max_spend:
            credits = int(raw)
            break
        print(f"  Enter 1-{max_spend}.")

    character["queued_action"] = {
        "character":     character["name"],
        "class":         character["class"],
        "weapon":        character["weapon"],
        "credits":       credits,
        "personalities": character["personalities"],
        "target":        target,
        "action_type":   action_type,
    }

    print(f"  -> {character['name']}: {action_type.upper()}"
          f"{' on ' + target if target else ''} ({credits} credits)")


# === TURN BUILDER — ENEMY AI ===
# Replace this function entirely for smarter AI.
# Signature: build_enemy_turn(enemies, squad, total_credits) -> (action_queue, new_pool)

def build_enemy_turn(enemies, squad, total_credits):
    """SIMPLE AI — random targets, credits split evenly, respects class caps."""
    alive_enemies = [e for e in enemies if e["hp"] > 0]
    alive_squad   = [c for c in squad   if c["hp"] > 0]

    if not alive_enemies or not alive_squad:
        return [], total_credits

    credits_each = total_credits // len(alive_enemies)
    remainder    = total_credits  % len(alive_enemies)

    action_queue = []

    for i, enemy in enumerate(alive_enemies):
        target      = random.choice(alive_squad)
        raw_credits = credits_each + (remainder if i == 0 else 0)
        cap         = CLASS_CREDIT_CAP[enemy["class"]]
        credits     = min(raw_credits, cap)

        if credits == 0:
            continue

        action_queue.append({
            "character":     enemy["name"],
            "class":         enemy["class"],
            "weapon":        enemy["weapon"],
            "credits":       credits,
            "personalities": enemy["personalities"],
            "target":        target["name"],
            "action_type":   "attack",
        })

    spent    = sum(a["credits"] for a in action_queue)
    leftover = total_credits - spent
    new_pool = min(leftover + CREDIT_START, CREDIT_CAP)

    return action_queue, new_pool


# === COMBAT RESOLVER ===

def resolve_turn(action_queue, targets, label="PLAYER"):
    """
    Calculates synergies silently then executes actions one by one.
    No phase headers printed — just actions as they happen.
    """

    # Silent pre-calculation
    condition_stack = []
    synergy_chains  = []
    current_chain   = []

    for action in action_queue:
        weapon_data = WEAPONS[action["weapon"]]

        if action["action_type"] == "catalyse":
            if current_chain:
                current_chain.append(action)
                synergy_chains.append(list(current_chain))
                current_chain = []
            continue

        if weapon_data["inflicts"]:
            condition_stack.append(weapon_data["inflicts"])
            current_chain.append(action)

        if weapon_data["exploits"]:
            if condition_stack:
                current_chain.append(action)
            else:
                current_chain = []

    if current_chain:
        synergy_chains.append(list(current_chain))

    # Silent synergy calculation
    valid_chains = [
        chain for chain in synergy_chains
        if any(WEAPONS[a["weapon"]]["exploits"] for a in chain
               if a["action_type"] != "catalyse")
    ]

    total_synergy = 0

    for chain in valid_chains:
        non_citro    = [a for a in chain if a["action_type"] != "catalyse"]
        citro_action = next(
            (a for a in chain if a["action_type"] == "catalyse"), None
        )

        personality_multiplier = 1.0
        for j in range(len(non_citro) - 1):
            personality_multiplier *= get_personality_multiplier(
                non_citro[j]["personalities"],
                non_citro[j + 1]["personalities"]
            )

        chain_credits    = sum(a["credits"] for a in non_citro)
        exploit_count    = len(condition_stack)
        citro_multiplier = 1.0

        if citro_action:
            citro_multiplier = calculate_citro_multiplier(citro_action["credits"])

        total_synergy += round(
            chain_credits * exploit_count *
            personality_multiplier * citro_multiplier,
            2
        )

    # Execution — one action at a time
    pause()
    print(f"\n  --- {label} TURN ---")

    active_conditions = []
    synergy_used      = False

    for action in action_queue:
        weapon_data = WEAPONS[action["weapon"]]
        base_damage = WEAPON_DAMAGE[action["weapon"]]
        credits     = action["credits"]
        is_splash   = weapon_data["type"] == "splash"

        time.sleep(1)

        if action["action_type"] == "catalyse":
            mult = calculate_citro_multiplier(credits)
            print(f"\n  {action['character']} catalyses ({credits} credits) — {mult}x")
            continue

        damage = int(base_damage * credits)

        if weapon_data["exploits"] and active_conditions and not synergy_used:
            final_damage = int(damage + total_synergy)
            synergy_used = True
            print(f"\n  {action['character']} SYNERGY EXPLOIT on {action['target']}"
                  f" — {final_damage} damage"
                  f" (base {damage} + {total_synergy} synergy)")
            active_conditions = []
        else:
            cond_str = ""
            if weapon_data["inflicts"]:
                cond_str = f" — inflicts {weapon_data['inflicts']}"
            print(f"\n  {action['character']} hits {action['target']}"
                  f" with {action['weapon']} for {damage} damage{cond_str}")

        if weapon_data["inflicts"]:
            active_conditions.append(weapon_data["inflicts"])

        target_char = next(
            (t for t in targets
             if t["name"] == action["target"] and t["hp"] > 0),
            None
        )

        if target_char:
            apply_damage(target_char, final_damage if synergy_used and
                         weapon_data["exploits"] else damage, targets, is_splash)

        if any(t["hp"] <= 0 for t in targets):
            defeated = [t["name"] for t in targets if t["hp"] <= 0]
            for name in defeated:
                print(f"  ** {name} defeated **")

    return all(t["hp"] <= 0 for t in targets)


# === MAIN COMBAT LOOP ===

def combat(squad, enemies):
    print("\n" + "#" * 50)
    print("  CITROGANG — COMBAT START")
    print("#" * 50)

    player_credits = CREDIT_START
    enemy_credits  = CREDIT_START
    turn           = 1

    while True:
        print(f"\n  === TURN {turn} ===")

        alive_squad   = [c for c in squad   if c["hp"] > 0]
        alive_enemies = [e for e in enemies if e["hp"] > 0]

        if not alive_squad:
            print("\n" + "#" * 50)
            print("  YOUR SQUAD HAS BEEN DEFEATED — GAME OVER")
            print("#" * 50)
            break

        if not alive_enemies:
            print("\n" + "#" * 50)
            print("  ALL ENEMIES DEFEATED — VICTORY")
            print("#" * 50)
            break

        # Player turn
        action_queue, player_credits = build_player_turn(
            squad, alive_enemies, player_credits
        )
        victory = resolve_turn(action_queue, enemies, label="PLAYER")

        if victory:
            print("\n" + "#" * 50)
            print("  ALL ENEMIES DEFEATED — VICTORY")
            print("#" * 50)
            break

        # Enemy turn
        alive_enemies = [e for e in enemies if e["hp"] > 0]
        alive_squad   = [c for c in squad   if c["hp"] > 0]

        if not alive_enemies or not alive_squad:
            break

        enemy_queue, enemy_credits = build_enemy_turn(
            alive_enemies, alive_squad, enemy_credits
        )
        defeat = resolve_turn(enemy_queue, squad, label="ENEMY")

        if defeat:
            print("\n" + "#" * 50)
            print("  YOUR SQUAD HAS BEEN DEFEATED — GAME OVER")
            print("#" * 50)
            break

        turn += 1


# === ENTRY POINT ===

if __name__ == "__main__":
    squad   = squad_selection()
    enemies = build_enemy_squad()

    print("\n  Enemy squad this fight:")
    for e in enemies:
        print(f"  {e['name']:12} {e['class'].upper():8}  WPN: {e['weapon']}")

    input("\n  Press Enter to begin...")
    combat(squad, enemies)