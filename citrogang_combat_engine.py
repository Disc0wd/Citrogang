# === CITROGANG COMBAT ENGINE ===

import time
import random
import copy

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
SWAP_COST    = 3
REPLACE_COST = 4


# === BASE ROSTERS ===

def make_player_roster():
    return [
        {"name": "Citro",  "class": "catalyst", "hp": 80,  "max_hp": 80,  "personalities": ["determined", "loyal"],     "is_citro": True,  "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Kaban",  "class": "heavy",    "hp": 100, "max_hp": 100, "personalities": ["stubborn",   "reckless"],   "is_citro": False, "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Vovk",   "class": "medium",   "hp": 75,  "max_hp": 75,  "personalities": ["charming",   "calculated"], "is_citro": False, "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Mykola", "class": "heavy",    "hp": 100, "max_hp": 100, "personalities": ["stubborn",   "loyal"],      "is_citro": False, "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Daryna", "class": "light",    "hp": 60,  "max_hp": 60,  "personalities": ["charming",   "volatile"],   "is_citro": False, "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Bohdan", "class": "medium",   "hp": 75,  "max_hp": 75,  "personalities": ["calculated", "stubborn"],   "is_citro": False, "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Oksana", "class": "light",    "hp": 60,  "max_hp": 60,  "personalities": ["reckless",   "volatile"],   "is_citro": False, "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Pavlo",  "class": "catalyst",    "hp": 100, "max_hp": 100, "personalities": ["reckless",   "charming"],   "is_citro": False, "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
    ]

def make_enemy_roster():
    return [
        {"name": "Razor",    "class": "heavy",  "hp": 100, "max_hp": 100, "personalities": ["volatile",   "stubborn"],   "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Brick",    "class": "heavy",  "hp": 100, "max_hp": 100, "personalities": ["reckless",   "volatile"],   "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Scar",     "class": "medium", "hp": 75,  "max_hp": 75,  "personalities": ["calculated", "charming"],   "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Knuckles", "class": "medium", "hp": 75,  "max_hp": 75,  "personalities": ["stubborn",   "loyal"],      "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Dart",     "class": "light",  "hp": 60,  "max_hp": 60,  "personalities": ["reckless",   "charming"],   "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Ghost",    "class": "light",  "hp": 60,  "max_hp": 60,  "personalities": ["calculated", "volatile"],   "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Tank",     "class": "heavy",  "hp": 100, "max_hp": 100, "personalities": ["stubborn",   "stubborn"],   "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
        {"name": "Viper",    "class": "medium", "hp": 75,  "max_hp": 75,  "personalities": ["volatile",   "charming"],   "weapon": None, "queued_action": None, "conditions": [], "soda_active": False},
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


def print_separator():
    print("\n" + "=" * 50)


def print_status(squad, enemies, player_credits, enemy_credits, inventory):
    print_separator()
    print(f"  YOUR CREDITS : {player_credits}/{CREDIT_CAP}")
    print(f"  ENEMY CREDITS: {enemy_credits}/{CREDIT_CAP}")
    print(f"  INVENTORY    : Soda x{inventory['soda']}  "
          f"Doshirak x{inventory['doshirak']}  "
          f"Borsch x{inventory['borsch']}")

    print("\n  YOUR SQUAD:")
    for i, c in enumerate(squad):
        if c["hp"] <= 0:
            print(f"  [{i+1}] {c['name']:12} DEFEATED")
        else:
            action     = c.get("queued_action")
            action_str = f" — [{action['action_type'].upper()}]" if action else ""
            soda_str   = " [SODA]" if c.get("soda_active") else ""
            cap        = CLASS_CREDIT_CAP[c["class"]]
            print(f"  [{i+1}] {c['name']:12} HP: {c['hp']:3}/{c['max_hp']:3}"
                  f"  {c['class'].upper():8}  WPN: {c['weapon'] or '?':10}"
                  f"  CAP:{cap}{soda_str}{action_str}")

    print("\n  ENEMIES:")
    for i, e in enumerate(enemies):
        if e["hp"] <= 0:
            print(f"  [{i+1}] {e['name']:12} DEFEATED")
        else:
            cond_str = f"  [{', '.join(e.get('conditions', []))}]" \
                       if e.get("conditions") else ""
            soda_str = " [SODA]" if e.get("soda_active") else ""
            print(f"  [{i+1}] {e['name']:12} HP: {e['hp']:3}/{e['max_hp']:3}"
                  f"  {e['class'].upper():8}  WPN: {e['weapon'] or '?':10}"
                  f"{soda_str}{cond_str}")
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

def squad_selection(player_roster):
    print("\n" + "#" * 50)
    print("  SQUAD SELECTION")
    print("#" * 50)
    print("  Select 4 characters in execution order.")
    print("  Slot 1 acts first, slot 4 acts last.\n")

    available_idx = list(range(len(player_roster)))
    squad         = []

    while len(squad) < 4:
        slot = len(squad) + 1
        print(f"\n  --- Slot {slot} ---")
        for i in available_idx:
            c   = player_roster[i]
            cap = CLASS_CREDIT_CAP[c["class"]]
            hp_str = f"HP: {c['hp']}/{c['max_hp']}" if c["hp"] < c["max_hp"] else "Full HP"
            print(f"  [{i+1}] {c['name']:12} {c['class'].upper():8}"
                  f"  {hp_str}  Traits: {', '.join(c['personalities'])}"
                  f"  Cap: {cap}")

        while True:
            raw = input("> ").strip()
            if raw.isdigit():
                idx = int(raw) - 1
                if idx in available_idx:
                    break
            print("  Invalid.")

        chosen = player_roster[idx]
        available_idx.remove(idx)

        weapons = CLASS_WEAPONS[chosen["class"]]
        print(f"\n  Weapon for {chosen['name']}:")
        for i, w in enumerate(weapons):
            wd = WEAPONS[w]
            print(f"  [{i+1}] {w:12}  inflicts: {wd['inflicts'] or 'EXPLOIT':10}"
                  f"  type: {wd['type']}")

        while True:
            raw = input("> ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(weapons):
                chosen["weapon"]        = weapons[int(raw) - 1]
                chosen["queued_action"] = None
                chosen["soda_active"]   = False
                break
            print("  Invalid.")

        squad.append(chosen)
        print(f"  -> Slot {slot}: {chosen['name']} ({chosen['weapon']})")

    print("\n  Final squad:")
    for i, c in enumerate(squad):
        print(f"  [{i+1}] {c['name']:12} {c['class'].upper():8}  WPN: {c['weapon']}")

    input("\n  Press Enter to start combat...")
    return squad


def build_enemy_squad(enemy_roster):
    selected = random.sample(
        [e for e in enemy_roster if e["hp"] > 0], min(4, len([e for e in enemy_roster if e["hp"] > 0]))
    )
    for e in selected:
        e["weapon"]        = random.choice(CLASS_WEAPONS[e["class"]])
        e["queued_action"] = None
        e["soda_active"]   = False
    return selected


# === PRE-TURN ACTIONS ===

def preturn_swap(squad, credits_remaining):
    """Swap two characters' positions. Costs SWAP_COST credits."""
    alive = [(i, c) for i, c in enumerate(squad) if c["hp"] > 0]
    if len(alive) < 2:
        print("  Not enough alive characters to swap.")
        return credits_remaining

    options = [f"{c['name']} (slot {i+1})" for i, c in alive]
    a_idx   = pick_from_list(f"Swap — select first character (cost: {SWAP_COST} credits):", options)
    if a_idx == -1:
        return credits_remaining

    b_options = [f"{c['name']} (slot {i+1})" for j, (i, c) in enumerate(alive) if j != a_idx]
    b_alive   = [(i, c) for j, (i, c) in enumerate(alive) if j != a_idx]
    b_idx     = pick_from_list("Swap — select second character:", b_options)
    if b_idx == -1:
        return credits_remaining

    pos_a = alive[a_idx][0]
    pos_b = b_alive[b_idx][0]

    squad[pos_a], squad[pos_b] = squad[pos_b], squad[pos_a]
    credits_remaining -= SWAP_COST

    print(f"  -> Swapped {squad[pos_a]['name']} (slot {pos_a+1})"
          f" and {squad[pos_b]['name']} (slot {pos_b+1})")
    print(f"  Credits remaining: {credits_remaining}")
    return credits_remaining


def preturn_replace(squad, player_roster, squad_names, dead_names, credits_remaining):
    alive_squad = [(i, c) for i, c in enumerate(squad) if c["hp"] > 0]
    available   = [c for c in player_roster
                   if c["name"] not in squad_names
                   and c["name"] not in dead_names
                   and c["hp"] > 0]

    if not available:
        print("  No available characters in roster.")
        return credits_remaining

    remove_opts = [f"{c['name']} (slot {i+1}, {c['class'].upper()}, HP: {c['hp']}/{c['max_hp']})"
                   for i, c in alive_squad]
    r_idx = pick_from_list(f"Replace — remove which? (cost: {REPLACE_COST} credits):", remove_opts)
    if r_idx == -1:
        return credits_remaining

    remove_pos = alive_squad[r_idx][0]
    removed    = squad[remove_pos]

    # Refund queued action
    refund = 0
    if removed.get("queued_action"):
        refund = removed["queued_action"]["credits"]
        removed["queued_action"] = None
        print(f"  Refunded {refund} credits from {removed['name']}'s queued action.")

    # Sync removed character's current HP back to their roster entry
    for r in player_roster:
        if r["name"] == removed["name"]:
            r["hp"]            = removed["hp"]
            r["soda_active"]   = False
            r["queued_action"] = None
            break

    # Choose incoming character
    in_opts = [f"{c['name']} ({c['class'].upper()}, HP: {c['hp']}/{c['max_hp']},"
               f" Traits: {', '.join(c['personalities'])})"
               for c in available]
    in_idx  = pick_from_list("Replace — bring in who?", in_opts)
    if in_idx == -1:
        # Cancelled — restore removed character
        for r in player_roster:
            if r["name"] == removed["name"]:
                squad[remove_pos] = r
                break
        return credits_remaining

    incoming = available[in_idx]
    weapons  = CLASS_WEAPONS[incoming["class"]]

    print(f"\n  Weapon for {incoming['name']}:")
    for i, w in enumerate(weapons):
        wd = WEAPONS[w]
        print(f"  [{i+1}] {w:12}  inflicts: {wd['inflicts'] or 'EXPLOIT':10}"
              f"  type: {wd['type']}")

    while True:
        raw = input("> ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(weapons):
            incoming["weapon"] = weapons[int(raw) - 1]
            break
        print("  Invalid.")

    incoming["queued_action"] = None
    incoming["soda_active"]   = False
    squad[remove_pos]         = incoming

    credits_remaining = credits_remaining - REPLACE_COST + refund

    print(f"  -> {removed['name']} returned to roster (HP: {removed['hp']}/{removed['max_hp']}).")
    print(f"  -> {incoming['name']} entered at slot {remove_pos+1} with {incoming['weapon']}.")
    print(f"  Credits remaining: {credits_remaining}")
    return credits_remaining


def preturn_consume(squad, inventory, credits_remaining, dead_in_squad):
    """Use a consumable on a squad member."""
    items = []
    if inventory["soda"]     > 0: items.append("Soda (1.5x next attack)")
    if inventory["doshirak"] > 0: items.append("Doshirak (regen 20% max HP)")
    if inventory["borsch"]   > 0 and dead_in_squad:
        items.append("Borsch (revive a defeated member)")

    if not items:
        print("  No usable consumables.")
        return credits_remaining

    choice = pick_from_list("Use consumable:", items)
    if choice == -1:
        return credits_remaining

    item_name = items[choice].split("(")[0].strip().lower()

    if item_name == "soda":
        alive = [c for c in squad if c["hp"] > 0]
        opts  = [f"{c['name']} ({c['class'].upper()})" for c in alive]
        t_idx = pick_from_list("Apply Soda to:", opts)
        if t_idx == -1:
            return credits_remaining
        alive[t_idx]["soda_active"] = True
        inventory["soda"] -= 1
        print(f"  -> Soda applied to {alive[t_idx]['name']} — 1.5x on next attack.")

    elif item_name == "doshirak":
        alive = [c for c in squad if c["hp"] > 0 and c["hp"] < c["max_hp"]]
        if not alive:
            print("  All characters are at full HP.")
            return credits_remaining
        opts  = [f"{c['name']} ({c['hp']}/{c['max_hp']} HP)" for c in alive]
        t_idx = pick_from_list("Apply Doshirak to:", opts)
        if t_idx == -1:
            return credits_remaining
        regen = int(alive[t_idx]["max_hp"] * 0.2)
        alive[t_idx]["hp"] = min(alive[t_idx]["max_hp"], alive[t_idx]["hp"] + regen)
        inventory["doshirak"] -= 1
        print(f"  -> {alive[t_idx]['name']} regenerated {regen} HP"
              f" (now {alive[t_idx]['hp']}/{alive[t_idx]['max_hp']}).")

    elif item_name == "borsch":
        dead  = [c for c in squad if c["hp"] <= 0]
        opts  = [f"{c['name']} ({c['class'].upper()})" for c in dead]
        t_idx = pick_from_list("Revive:", opts)
        if t_idx == -1:
            return credits_remaining
        dead[t_idx]["hp"] = int(dead[t_idx]["max_hp"] * 0.5)
        inventory["borsch"] -= 1
        print(f"  -> {dead[t_idx]['name']} revived with"
              f" {dead[t_idx]['hp']}/{dead[t_idx]['max_hp']} HP.")

    return credits_remaining


# === TURN BUILDER — PLAYER ===

def build_player_turn(squad, enemies, total_credits, inventory,
                      player_roster, dead_names):
    credits_remaining = total_credits

    for c in squad:
        c["queued_action"] = None

    while True:
        squad_names    = {c["name"] for c in squad}
        dead_in_squad  = [c for c in squad if c["hp"] <= 0]

        print_status(squad, enemies, credits_remaining, "?", inventory)

        print("  ACTIONS:")
        print("  [1-4] Assign action to squad member")
        print("  [S]   Swap order         (3 credits)")
        print("  [R]   Replace character  (4 credits)")
        print("  [U]   Use consumable")
        print("  [C]   Commit turn")
        print("  [X]   Reset all actions")

        cmd = input("> ").strip().lower()

        if cmd == "c":
            locked = [c for c in squad if c.get("queued_action") and c["hp"] > 0]
            if not locked:
                print("  No actions queued.")
                continue
            citro = next(
                (c for c in squad if c.get("queued_action")
                 and c["queued_action"]["action_type"] == "catalyse"),
                None
            )
            if citro:
                order = [c for c in squad if c.get("queued_action") and c["hp"] > 0]
                if order[-1]["name"] != citro["name"]:
                    print("\n  !! WARNING: Citro is catalysing but not last."
                          " Commit anyway? [Y/N]")
                    if input("> ").strip().lower() != "y":
                        continue
            print(f"\n  Committing {len(locked)} action(s).")
            break

        elif cmd == "x":
            for c in squad:
                c["queued_action"] = None
            credits_remaining = total_credits
            print("  Actions reset.")

        elif cmd == "s":
            if credits_remaining < SWAP_COST:
                print(f"  Not enough credits (need {SWAP_COST}).")
            else:
                credits_remaining = preturn_swap(squad, credits_remaining)

        elif cmd == "r":
            if credits_remaining < REPLACE_COST:
                print(f"  Not enough credits (need {REPLACE_COST}).")
            else:
                credits_remaining = preturn_replace(
                    squad, player_roster, squad_names, dead_names, credits_remaining
                )

        elif cmd == "u":
            credits_remaining = preturn_consume(
                squad, inventory, credits_remaining, dead_in_squad
            )

        elif cmd.isdigit() and 1 <= int(cmd) <= len(squad):
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
    if character["class"] == "catalyst":
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
        opts  = [f"{e['name']} (HP: {e['hp']}, WPN: {e['weapon']})"
                 for e in alive_enemies]
        t_idx = pick_from_list("Target:", opts)
        if t_idx == -1:
            return
        target = alive_enemies[t_idx]["name"]

    if credits_remaining <= 0:
        print("  No credits remaining.")
        return

    cap       = CLASS_CREDIT_CAP[character["class"]]
    max_spend = min(credits_remaining, cap)

    print(f"\n  Available: {credits_remaining}  Cap: {cap}  Max: {max_spend}")
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
        "soda_active":   character.get("soda_active", False),
    }
    character["soda_active"] = False

    print(f"  -> {character['name']}: {action_type.upper()}"
          f"{' on ' + target if target else ''} ({credits} credits)")


# === TURN BUILDER — ENEMY AI ===
# Replace this function entirely for smarter AI.
# Signature: build_enemy_turn(enemies, squad, total_credits, inventory,
#                             enemy_roster, dead_names) -> (action_queue, new_pool)

def build_enemy_turn(enemies, squad, total_credits, inventory,
                     enemy_roster, dead_names):
    """SIMPLE AI — random decisions for all mechanics."""
    alive_enemies = [e for e in enemies if e["hp"] > 0]
    alive_squad   = [c for c in squad   if c["hp"] > 0]

    if not alive_enemies or not alive_squad:
        return [], total_credits

    credits_remaining = total_credits

    # 20% chance to use a consumable
    if random.random() < 0.2:
        credits_remaining = enemy_consume(
            enemies, inventory, alive_squad, credits_remaining
        )

    # 10% chance to swap order if enough credits
    if credits_remaining >= SWAP_COST and len(alive_enemies) >= 2 and random.random() < 0.1:
        i, j = random.sample(range(len(alive_enemies)), 2)
        enemies[i], enemies[j] = enemies[j], enemies[i]
        credits_remaining -= SWAP_COST
        print(f"  [ENEMY] Swapped {enemies[i]['name']} and {enemies[j]['name']}.")

    # 10% chance to replace a character if enough credits
    available_replacements = [
        e for e in enemy_roster
        if e["name"] not in {en["name"] for en in enemies}
        and e["name"] not in dead_names
        and e["hp"] > 0
    ]
    if (credits_remaining >= REPLACE_COST and available_replacements
            and alive_enemies and random.random() < 0.1):
        slot_idx  = random.randrange(len(alive_enemies))
        removed   = alive_enemies[slot_idx]
        incoming  = random.choice(available_replacements)
        incoming["weapon"]        = random.choice(CLASS_WEAPONS[incoming["class"]])
        incoming["queued_action"] = None
        incoming["soda_active"]   = False

        # Find and replace in main enemies list
        for i, e in enumerate(enemies):
            if e["name"] == removed["name"]:
                enemies[i] = incoming
                break

        credits_remaining -= REPLACE_COST
        print(f"  [ENEMY] Replaced {removed['name']} with {incoming['name']}.")

    # Build action queue
    alive_enemies = [e for e in enemies if e["hp"] > 0]
    credits_each  = credits_remaining // len(alive_enemies) if alive_enemies else 0
    remainder     = credits_remaining  % len(alive_enemies) if alive_enemies else 0

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
            "soda_active":   enemy.get("soda_active", False),
        })
        enemy["soda_active"] = False

    spent    = sum(a["credits"] for a in action_queue)
    leftover = credits_remaining - spent
    new_pool = min(leftover + CREDIT_START, CREDIT_CAP)

    return action_queue, new_pool


def enemy_consume(enemies, inventory, alive_squad, credits_remaining):
    """Enemy randomly uses a consumable."""
    alive_enemies = [e for e in enemies if e["hp"] > 0]
    options       = []

    if inventory["enemy_soda"]     > 0 and alive_enemies:
        options.append("soda")
    if inventory["enemy_doshirak"] > 0:
        injured = [e for e in alive_enemies if e["hp"] < e["max_hp"]]
        if injured:
            options.append("doshirak")
    if inventory["enemy_borsch"]   > 0:
        dead = [e for e in enemies if e["hp"] <= 0]
        if dead:
            options.append("borsch")

    if not options:
        return credits_remaining

    choice = random.choice(options)

    if choice == "soda":
        target = random.choice(alive_enemies)
        target["soda_active"] = True
        inventory["enemy_soda"] -= 1
        print(f"  [ENEMY] Used Soda on {target['name']}.")

    elif choice == "doshirak":
        injured = [e for e in alive_enemies if e["hp"] < e["max_hp"]]
        target  = random.choice(injured)
        regen   = int(target["max_hp"] * 0.2)
        target["hp"] = min(target["max_hp"], target["hp"] + regen)
        inventory["enemy_doshirak"] -= 1
        print(f"  [ENEMY] Used Doshirak on {target['name']}"
              f" (+{regen} HP, now {target['hp']}/{target['max_hp']}).")

    elif choice == "borsch":
        dead   = [e for e in enemies if e["hp"] <= 0]
        target = random.choice(dead)
        target["hp"] = int(target["max_hp"] * 0.5)
        inventory["enemy_borsch"] -= 1
        print(f"  [ENEMY] Used Borsch on {target['name']}"
              f" (revived at {target['hp']}/{target['max_hp']}).")

    return credits_remaining


# === COMBAT RESOLVER ===

def resolve_turn(action_queue, targets, label="PLAYER"):
    """Calculates synergies silently, executes actions one by one."""

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

    valid_chains  = [
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
        citro_multiplier = (calculate_citro_multiplier(citro_action["credits"])
                            if citro_action else 1.0)

        total_synergy += round(
            chain_credits * len(condition_stack) *
            personality_multiplier * citro_multiplier,
            2
        )

    # Execution
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

        # Apply soda multiplier
        if action.get("soda_active"):
            damage = int(damage * 1.5)

        if weapon_data["exploits"] and active_conditions and not synergy_used:
            final_damage = int(damage + total_synergy)
            synergy_used = True
            soda_str     = " [SODA BOOSTED]" if action.get("soda_active") else ""
            print(f"\n  {action['character']} SYNERGY EXPLOIT on {action['target']}"
                  f" — {final_damage} damage"
                  f" (base {damage} + {total_synergy} synergy){soda_str}")
            active_conditions = []
        else:
            cond_str = f" — inflicts {weapon_data['inflicts']}" \
                       if weapon_data["inflicts"] else ""
            soda_str = " [SODA]" if action.get("soda_active") else ""
            final_damage = damage
            print(f"\n  {action['character']} hits {action['target']}"
                  f" with {action['weapon']} for {damage} damage{cond_str}{soda_str}")

        if weapon_data["inflicts"]:
            active_conditions.append(weapon_data["inflicts"])

        target_char = next(
            (t for t in targets
             if t["name"] == action["target"] and t["hp"] > 0),
            None
        )

        if target_char:
            apply_damage(target_char, final_damage, targets, is_splash)

        newly_defeated = [t["name"] for t in targets
                          if t["hp"] <= 0 and t.get("_was_alive", True)]
        for t in targets:
            if t["hp"] <= 0:
                t["_was_alive"] = False

        for name in newly_defeated:
            print(f"  ** {name} defeated **")

    return all(t["hp"] <= 0 for t in targets)


# === MAIN COMBAT LOOP ===

def combat(squad, enemies, player_roster, enemy_roster):
    print("\n" + "#" * 50)
    print("  CITROGANG — COMBAT START")
    print("#" * 50)

    player_credits = CREDIT_START
    enemy_credits  = CREDIT_START

    player_inventory = {"soda": 2, "doshirak": 2, "borsch": 1}
    enemy_inventory  = {"enemy_soda": 2, "enemy_doshirak": 2, "enemy_borsch": 1}

    player_dead = set()
    enemy_dead  = set()

    # Mark all targets as alive initially
    for c in squad:   c["_was_alive"] = True
    for e in enemies: e["_was_alive"] = True

    turn = 1

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

        # Track dead names
        player_dead = {c["name"] for c in squad        if c["hp"] <= 0}
        enemy_dead  = {e["name"] for e in enemies      if e["hp"] <= 0}

        squad_names = {c["name"] for c in squad}

        # Player turn
        action_queue, player_credits = build_player_turn(
            squad, alive_enemies, player_credits,
            player_inventory, player_roster, player_dead
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
            enemies, alive_squad, enemy_credits,
            enemy_inventory, enemy_roster, enemy_dead
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
    player_roster = make_player_roster()
    enemy_roster  = make_enemy_roster()

    squad   = squad_selection(player_roster)
    enemies = build_enemy_squad(enemy_roster)

    print("\n  Enemy squad this fight:")
    for e in enemies:
        print(f"  {e['name']:12} {e['class'].upper():8}  WPN: {e['weapon']}")

    input("\n  Press Enter to begin...")
    combat(squad, enemies, player_roster, enemy_roster)