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
    "bat":       25,
    "chain":     20,
    "belt":      18,
    "knuckles":  15,
    "slingshot": 12,
    "brick":     10,
}

CLASS_WEAPONS = {
    "heavy":  ["bat", "chain"],
    "medium": ["belt", "knuckles"],
    "light":  ["slingshot", "brick"],
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


# === HELPER FUNCTIONS ===

def get_personality_multiplier(traits_a, traits_b):
    best = 1.0
    for t1 in traits_a:
        for t2 in traits_b:
            key = tuple(sorted([t1, t2]))
            value = PERSONALITY_MULTIPLIERS.get(key, 1.0)
            if value > best:
                best = value
    return best


def calculate_citro_multiplier(credits):
    base    = 1.0 + (credits * 0.25)
    penalty = max(0, credits - 3) * 0.1
    return round(base - penalty, 2)


def validate_loadout(character_class, weapon):
    return weapon in CLASS_WEAPONS.get(character_class, [])


def describe_condition(condition):
    return CONDITION_DESCRIPTIONS.get(condition, "unknown condition")


def print_separator():
    print("\n" + "=" * 50)


def pause():
    time.sleep(3)


def apply_damage(target, damage, targets, splash):
    """
    Apply damage to a target.
    If splash: primary target takes 50%, remainder split evenly among others.
    If concentrated: full damage to target only.
    """
    if splash:
        alive_others = [t for t in targets if t["hp"] > 0 and t["name"] != target["name"]]
        primary_dmg  = damage // 2
        other_dmg    = (damage // 2) // len(alive_others) if alive_others else 0

        target["hp"] = max(0, target["hp"] - primary_dmg)
        print(f"         {target['name']}: -{primary_dmg} HP  (remaining: {target['hp']})")

        for t in alive_others:
            if other_dmg > 0:
                t["hp"] = max(0, t["hp"] - other_dmg)
                print(f"         {t['name']}: -{other_dmg} HP  (remaining: {t['hp']})")
    else:
        target["hp"] = max(0, target["hp"] - damage)
        print(f"         {target['name']}: -{damage} HP  (remaining: {target['hp']})")


def print_status(squad, enemies, player_credits, enemy_credits):
    print_separator()
    print(f"  YOUR CREDITS : {player_credits}/{CREDIT_CAP}")
    print(f"  ENEMY CREDITS: {enemy_credits}/{CREDIT_CAP}")

    print("\n  YOUR SQUAD:")
    for i, c in enumerate(squad):
        if c["hp"] <= 0:
            print(f"  [{i+1}] {c['name']:12} HP: DEFEATED")
        else:
            action     = c.get("queued_action")
            action_str = f" — [{action['action_type'].upper()}]" if action else ""
            print(f"  [{i+1}] {c['name']:12} HP: {c['hp']:3}/{c['max_hp']:3}"
                  f"  WPN: {c['weapon']:10}{action_str}")

    print("\n  ENEMIES:")
    for i, e in enumerate(enemies):
        if e["hp"] <= 0:
            print(f"  [{i+1}] {e['name']:12} HP: DEFEATED")
        else:
            conditions = e.get("conditions", [])
            cond_str   = f"  [{', '.join(conditions)}]" if conditions else ""
            print(f"  [{i+1}] {e['name']:12} HP: {e['hp']:3}/{e['max_hp']:3}"
                  f"  WPN: {e['weapon']:10}{cond_str}")
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


# === TURN BUILDER — PLAYER ===

def build_player_turn(squad, enemies, total_credits):
    credits_remaining = total_credits

    for c in squad:
        c["queued_action"] = None

    while True:
        print_status(squad, enemies, credits_remaining, "?")

        print("  ACTIONS:")
        print("  [1-4] Select squad member to assign action")
        print("  [C]   Commit turn")
        print("  [R]   Reset all actions")

        cmd = input("> ").strip().lower()

        if cmd == "c":
            locked = [c for c in squad if c.get("queued_action") and c["hp"] > 0]
            if not locked:
                print("  No actions queued. Assign at least one action first.")
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
                    print("\n  !! WARNING: Citro is catalysing but is not last in"
                          " the execution order.")
                    print("     Catalyst will fire before the synergy chain resolves.")
                    print("     Commit anyway? [Y/N]")
                    confirm = input("> ").strip().lower()
                    if confirm != "y":
                        continue

            print(f"\n  Committing turn with {len(locked)} action(s).")
            break

        if cmd == "r":
            for c in squad:
                c["queued_action"] = None
            credits_remaining = total_credits
            print("  All actions reset.")
            continue

        if cmd.isdigit() and 1 <= int(cmd) <= len(squad):
            idx       = int(cmd) - 1
            character = squad[idx]

            if character["hp"] <= 0:
                print(f"  {character['name']} is defeated.")
                continue

            if character.get("queued_action"):
                print(f"  {character['name']} already has an action queued."
                      " Reset to change.")
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
        print(f"\n  {leftover} unspent credit(s) carried over."
              f" Next turn pool: {new_pool}/{CREDIT_CAP}")

    return action_queue, new_pool


def assign_action(character, enemies, credits_remaining):
    print(f"\n  Assigning action for: {character['name'].upper()}")

    options = ["Attack"]
    if character.get("is_citro"):
        options.append("Catalyse")

    choice = pick_from_list("Choose action type:", options)
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
        t_idx = pick_from_list("Choose target:", target_names)
        if t_idx == -1:
            return
        target = alive_enemies[t_idx]["name"]

    if credits_remaining <= 0:
        print("  No credits remaining.")
        return

    print(f"\n  Credits available: {credits_remaining}")
    print(f"  How many credits to spend? (1-{credits_remaining})")
    while True:
        raw = input("> ").strip()
        if raw.isdigit() and 1 <= int(raw) <= credits_remaining:
            credits = int(raw)
            break
        print(f"  Enter a number between 1 and {credits_remaining}.")

    character["queued_action"] = {
        "character":     character["name"],
        "class":         character["class"],
        "weapon":        character["weapon"],
        "credits":       credits,
        "personalities": character["personalities"],
        "target":        target,
        "action_type":   action_type,
    }

    print(f"  {character['name']} queued: {action_type.upper()}"
          f"{' on ' + target if target else ''} ({credits} credits)")


# === TURN BUILDER — ENEMY (SIMPLE AI) ===
# Replace this function entirely for medium/smart AI.
# Signature must stay: build_enemy_turn(enemies, squad, total_credits) -> (action_queue, new_pool)

def build_enemy_turn(enemies, squad, total_credits):
    """
    SIMPLE AI — v1.0 alpha.
    Each alive enemy attacks a random alive squad member.
    Credits distributed evenly, remainder to first enemy.
    """
    alive_enemies = [e for e in enemies if e["hp"] > 0]
    alive_squad   = [c for c in squad   if c["hp"] > 0]

    if not alive_enemies or not alive_squad:
        return [], total_credits

    credits_each = total_credits // len(alive_enemies)
    remainder    = total_credits  % len(alive_enemies)

    action_queue = []

    for i, enemy in enumerate(alive_enemies):
        target  = random.choice(alive_squad)
        credits = credits_each + (remainder if i == 0 else 0)

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
    Resolves a full turn for either player or enemy.
    targets = characters being attacked (enemies for player, squad for enemy).
    """

    # PRE-CALCULATION
    pause()
    print_separator()
    print(f"PRE-CALCULATION PHASE — {label}")
    print_separator()

    condition_stack = []
    synergy_chains  = []
    current_chain   = []

    for i, action in enumerate(action_queue):
        weapon_data = WEAPONS[action["weapon"]]

        print(f"\n  [{i+1}] {action['character'].upper()}")
        print(f"      action  : {action['action_type']}")
        print(f"      weapon  : {action['weapon']}")
        print(f"      credits : {action['credits']}")
        if action["target"]:
            print(f"      target  : {action['target']}")

        if action["action_type"] == "catalyse":
            print(f"      role    : CATALYST")
            if current_chain:
                current_chain.append(action)
                synergy_chains.append(list(current_chain))
                current_chain = []
            else:
                print(f"      !! catalyst fired with no open chain — no effect")
            continue

        if weapon_data["inflicts"]:
            condition = weapon_data["inflicts"]
            condition_stack.append(condition)
            current_chain.append(action)
            print(f"      inflicts: {condition} — {describe_condition(condition)}")

        if weapon_data["exploits"]:
            if condition_stack:
                print(f"      exploits: {len(condition_stack)} condition(s)"
                      f" — {condition_stack}")
                current_chain.append(action)
            else:
                print(f"      exploits: no conditions — normal attack")
                current_chain = []

    if current_chain:
        synergy_chains.append(list(current_chain))

    # SYNERGY CALCULATION
    pause()
    print_separator()
    print(f"SYNERGY CALCULATION — {label}")
    print_separator()

    valid_chains = [
        chain for chain in synergy_chains
        if any(WEAPONS[a["weapon"]]["exploits"] for a in chain
               if a["action_type"] != "catalyse")
    ]

    all_synergy_values = []

    if not valid_chains:
        print("\n  No synergies detected.")
    else:
        for chain in valid_chains:
            non_citro    = [a for a in chain if a["action_type"] != "catalyse"]
            citro_action = next(
                (a for a in chain if a["action_type"] == "catalyse"), None
            )

            print(f"\n  Chain: {[a['character'] for a in chain]}")

            personality_multiplier = 1.0
            for j in range(len(non_citro) - 1):
                a         = non_citro[j]
                b         = non_citro[j + 1]
                pair_mult = get_personality_multiplier(
                    a["personalities"], b["personalities"]
                )
                print(f"  {a['character']} + {b['character']} = {pair_mult}x")
                personality_multiplier *= pair_mult

            chain_credits    = sum(a["credits"] for a in non_citro)
            exploit_count    = len(condition_stack)
            citro_multiplier = 1.0

            if citro_action:
                citro_multiplier = calculate_citro_multiplier(citro_action["credits"])
                print(f"  citro catalyst: {citro_action['credits']}"
                      f" credits = {citro_multiplier}x")

            synergy_value = round(
                chain_credits    *
                exploit_count    *
                personality_multiplier *
                citro_multiplier,
                2
            )

            print(f"\n  chain credits      : {chain_credits}")
            print(f"  conditions stacked : {exploit_count}")
            print(f"  personality mult   : {round(personality_multiplier, 2)}x")
            print(f"  citro catalyst     : {citro_multiplier}x")
            print(f"  SYNERGY VALUE      : {synergy_value}")

            all_synergy_values.append(synergy_value)

    total_synergy = sum(all_synergy_values)

    # EXECUTION
    pause()
    print_separator()
    print(f"EXECUTION PHASE — {label}")
    print_separator()

    active_conditions = []
    synergy_used      = False

    for i, action in enumerate(action_queue):
        weapon_data = WEAPONS[action["weapon"]]
        base_damage = WEAPON_DAMAGE[action["weapon"]]
        credits     = action["credits"]
        is_splash   = weapon_data["type"] == "splash"

        time.sleep(1)
        print(f"\n  [{i+1}] {action['character'].upper()}")

        if action["action_type"] == "catalyse":
            mult = calculate_citro_multiplier(credits)
            print(f"      >> CATALYSE — {mult}x catalyst applied")
            print(f"         animation: CATALYST_GLOW")
            continue

        damage = int(base_damage * credits)

        if weapon_data["exploits"] and active_conditions and not synergy_used:
            final_damage = int(damage + total_synergy)
            synergy_used = True
            print(f"      >> SYNERGY EXPLOIT")
            print(f"         base damage    : {damage}")
            print(f"         synergy bonus  : {total_synergy}")
            print(f"         total damage   : {final_damage}")
            print(f"         animation      : EXPLOIT + SYNERGY_FLASH")
            active_conditions = []
        else:
            final_damage = damage
            print(f"      >> attacks {action['target']} for {final_damage} damage")

        if weapon_data["inflicts"]:
            cond = weapon_data["inflicts"]
            active_conditions.append(cond)
            print(f"         inflicts {cond} — {describe_condition(cond)}")
            print(f"         animation: {cond}_HIT")

        target_char = next(
            (t for t in targets
             if t["name"] == action["target"] and t["hp"] > 0),
            None
        )

        if target_char:
            apply_damage(target_char, final_damage, targets, is_splash)

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
            print("\n  YOUR SQUAD HAS BEEN DEFEATED.")
            print("  GAME OVER.")
            break

        if not alive_enemies:
            print("\n  ALL ENEMIES DEFEATED — VICTORY.")
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


# === ROSTER ===

if __name__ == "__main__":

    squad = [
        {
            "name":          "Kaban",
            "class":         "heavy",
            "weapon":        "chain",
            "hp":            100,
            "max_hp":        100,
            "personalities": ["stubborn", "reckless"],
            "is_citro":      False,
            "queued_action": None,
        },
        {
            "name":          "Vovk",
            "class":         "medium",
            "weapon":        "belt",
            "hp":            75,
            "max_hp":        75,
            "personalities": ["charming", "calculated"],
            "is_citro":      False,
            "queued_action": None,
        },
        {
            "name":          "Recruit",
            "class":         "light",
            "weapon":        "brick",
            "hp":            60,
            "max_hp":        60,
            "personalities": ["volatile", "reckless"],
            "is_citro":      False,
            "queued_action": None,
        },
        {
            "name":          "Citro",
            "class":         "heavy",
            "weapon":        "bat",
            "hp":            80,
            "max_hp":        80,
            "personalities": ["determined", "loyal"],
            "is_citro":      True,
            "queued_action": None,
        },
    ]

    enemies = [
        {
            "name":          "Bully",
            "class":         "heavy",
            "weapon":        "bat",
            "hp":            200,
            "max_hp":        200,
            "personalities": ["stubborn", "volatile"],
            "conditions":    [],
        },
        {
            "name":          "Thug_1",
            "class":         "medium",
            "weapon":        "knuckles",
            "hp":            80,
            "max_hp":        80,
            "personalities": ["reckless", "charming"],
            "conditions":    [],
        },
        {
            "name":          "Thug_2",
            "class":         "light",
            "weapon":        "brick",
            "hp":            80,
            "max_hp":        80,
            "personalities": ["volatile", "calculated"],
            "conditions":    [],
        },
    ]

    combat(squad, enemies)