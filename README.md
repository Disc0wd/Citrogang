# Citrogang — Combat Engine

> Prototype combat engine for **Citrogang**, a turn-based tactics RPG by Purify Games.
> Built in Python as a design and logic prototype before full implementation in Godot 4.

-----

## Table of Contents

- [What is Citrogang?](#what-is-citrogang)
- [About this repository](#about-this-repository)
- [Running the prototype](#running-the-prototype)
- [Combat system overview](#combat-system-overview)
  - [Two-phase turns](#two-phase-turns)
  - [Attack credits](#attack-credits)
  - [Classes and weapons](#classes-and-weapons)
  - [Condition stack](#condition-stack)
  - [Synergy chains](#synergy-chains)
  - [Personality system](#personality-system)
  - [Citro — the catalyst](#citro--the-catalyst)
  - [Enemy AI](#enemy-ai)
  - [Credit carryover](#credit-carryover)
- [What is implemented](#what-is-implemented)
- [What is not yet implemented](#what-is-not-yet-implemented)
- [Full game — planned implementation](#full-game--planned-implementation)

-----

## What is Citrogang?

**Citrogang** is a turn-based tactics RPG set in a fictional post-Soviet Eastern European city. A teenager’s bottle of сітро — a Soviet-era lemon soft drink — gets stolen by a local bully. He assembles a street gang and crosses five city districts to get it back.

The game features deep invisible systems — mechanics that are never explained to the player and are discovered entirely through play, failure, and observation.

-----

## About this repository

This repository contains the standalone combat engine prototype written in Python. It is not the full game. It is a playable proof-of-concept for the combat system, used to validate design decisions before Godot 4 implementation begins.

-----

## Running the prototype

**Requirements:** Python 3.x

```bash
git clone https://github.com/Disc0wd/Citrogang.git
cd Citrogang
python citrogang_combat_engine.py
```

### Controls

|Input          |Action                          |
|---------------|--------------------------------|
|`1` `2` `3` `4`|Select squad member             |
|`1` `2` `3`    |Select action / target / credits|
|`C`            |Commit turn                     |
|`R`            |Reset all actions               |
|`0`            |Back                            |

-----

## Combat System Overview

### Two-phase turns

Every turn is split into two phases:

1. **Pre-planning** — the player assigns actions to squad members from a shared credit pool and commits the turn
1. **Execution** — the engine scans the full queue, detects synergy chains, calculates all values, then resolves actions top to bottom in configured order

### Attack credits

A shared pool of credits is distributed across squad members each turn.

|Property          |Value                              |
|------------------|-----------------------------------|
|Starting pool     |10                                 |
|Maximum pool (cap)|15                                 |
|Carryover         |Unspent credits carry to next turn |
|Overflow          |Credits exceeding cap are discarded|

More credits spent on a character means more damage and more synergy contribution. Choosing how to distribute credits is the core tactical decision every turn. Both the player and enemy have independent pools with the same rules.

### Classes and weapons

Three character classes, each restricted to two weapons:

|Class |Weapon   |Base damage|Coverage    |
|------|---------|-----------|------------|
|Heavy |Bat      |20         |Concentrated|
|Heavy |Chain    |20         |Splash      |
|Medium|Belt     |15         |Concentrated|
|Medium|Knuckles |15         |Splash      |
|Light |Slingshot|10         |Concentrated|
|Light |Brick    |10         |Splash      |

Weapons within the same class deal equal damage. The difference is coverage type and the condition inflicted.

**Coverage types:**

- **Concentrated** — full damage to primary target only
- **Splash** — 50% damage to primary target, remaining 50% split evenly among other alive targets

### Condition stack

Five weapons inflict status conditions onto the target. One weapon — the **brick** — exploits them.

|Weapon   |Inflicts   |Description                           |
|---------|-----------|--------------------------------------|
|Bat      |`STAGGER`  |Off balance, vulnerable to follow-up  |
|Chain    |`RESTRAIN` |Movement locked, easier to hit        |
|Belt     |`EXPOSE`   |Defence lowered                       |
|Knuckles |`BREAK`    |Armour or guard compromised           |
|Slingshot|`DISORIENT`|Accuracy reduced, may miss next turn  |
|Brick    |*(exploit)*|Cashes out all conditions on the stack|

When the brick fires, it reads the current condition stack on the target and converts stacked conditions into bonus damage. More conditions stacked means a more powerful exploit.

### Synergy chains

When condition-inflicting weapons are followed by the brick in execution order, the engine detects a synergy chain during pre-calculation.

**Synergy formula:**

```
synergy value = chain credits × conditions stacked × personality multiplier × citro catalyst
```

Chains can be 2, 3, or 4 weapons long. The synergy ruleset is **never shown to the player** — it is learned entirely through play.

**Example — full 4-weapon chain:**

```
Kaban  (chain   — RESTRAIN, 2 credits)
Vovk   (belt    — EXPOSE,   2 credits)
Recruit(brick   — EXPLOIT,  3 credits)
Citro  (catalyse,           3 credits)

Synergy: 7 credits × 2 conditions × 3.0x personality × 1.75x catalyst = 73.5
```

### Personality system

Each character has **two personality traits** from six types:

`Stubborn` `Reckless` `Charming` `Calculated` `Loyal` `Volatile`

When two characters are adjacent in the execution order, their trait combination produces a multiplier applied to the synergy calculation. Multipliers compound across the full chain.

|Pair                 |Multiplier|Chemistry                                  |
|---------------------|----------|-------------------------------------------|
|Volatile + Volatile  |2.3x      |Two unstable forces near implosion         |
|Reckless + Reckless  |2.2x      |Chaos amplifies chaos                      |
|Reckless + Volatile  |2.1x      |Explosive instability                      |
|Calculated + Volatile|2.0x      |Opposites create explosive results         |
|Stubborn + Volatile  |1.7x      |Stubbornness contains volatility into power|
|Loyal + Loyal        |1.5x      |Mutual trust compounds reliably            |
|Loyal + Volatile     |0.7x      |Loyalty destabilised *(negative)*          |
|Reckless + Calculated|0.8x      |Planning disrupted *(negative)*            |
|Charming + Stubborn  |0.9x      |Charm bounces off stubbornness *(negative)*|


> The full multiplier table is hidden from the player and learned through experience.

### Citro — the catalyst

Citro is the protagonist and a unique **Catalyst** class character. Each turn he can:

- **Attack** — acts as a normal Heavy character, contributing conditions to a chain
- **Catalyse** — amplifies the synergy value of the chain that precedes him in execution order

**Rules:**

- Citro must be placed **last** in the queue for the catalyst to apply
- Catalysing with no open chain before him has no effect
- The game **warns** the player if Citro is out of position but allows the commit

**Catalyst multiplier curve:**

|Credits spent|Multiplier          |
|-------------|--------------------|
|1            |1.25x               |
|2            |1.50x               |
|3            |1.75x *(sweet spot)*|
|4            |1.90x               |
|5            |2.00x               |

Diminishing returns above 3 credits make loading the chain itself more valuable than maxing Citro’s catalyst.

### Enemy AI

Enemies use the **same combat engine** as the player — same classes, weapons, personality traits, and synergy system. The current AI is a simple placeholder:

- Credits distributed evenly across alive enemies
- Targets chosen at random from alive squad members

The AI is fully isolated in a single function `build_enemy_turn()` with a fixed signature, designed to be **replaced entirely** without touching the rest of the engine.

```python
# Signature is fixed — swap internals freely
def build_enemy_turn(enemies, squad, total_credits) -> (action_queue, new_pool):
    ...
```

### Credit carryover

Both player and enemy carry unspent credits into the next turn.

```
new pool = min(unspent + 10, 15)
```

Conservative spending builds toward a power turn. Credits exceeding the cap of 15 are discarded.

-----

## What is implemented

- [x] Full turn builder with credit allocation and action assignment
- [x] Condition stack and synergy chain detection
- [x] Personality multiplier system — all 21 unique trait pairs
- [x] Citro catalyst with diminishing returns curve
- [x] Splash damage — 50% primary / 50% split among others
- [x] Credit carryover with cap for both player and enemy
- [x] Enemy characters with full data structure — class, weapon, personalities
- [x] Simple enemy AI using the same combat resolver as the player
- [x] Win and loss conditions
- [x] Multi-turn combat loop
- [x] Phase delays — 3 seconds per phase, 1 second per action during execution
- [x] Citro misplacement warning on commit

-----

## What is not yet implemented

- [ ] Neglect meter and hidden hesitation thresholds
- [ ] Internal social graph between squad members
- [ ] Mid-fight squad swaps
- [ ] Consume action
- [ ] Enemy AI — medium tier (fixed synergy patterns per faction)
- [ ] Enemy AI — smart tier (synergy-aware targeting and counterplay)
- [ ] Balance pass on damage numbers and enemy HP
- [ ] Character progression and trait unlocking
- [ ] Pre-battle weapon assignment and order configuration
- [ ] Full character roster beyond placeholder characters

-----

## Full game — planned implementation

|Property   |Detail                                   |
|-----------|-----------------------------------------|
|Engine     |Godot 4.5                                |
|Language   |GDScript (translated from this prototype)|
|Art style  |2D pixel art — Pokemon HGSS perspective  |
|Asset base |Limezu Modern Exteriors / Interiors / UI |
|Resolution |640×360                                  |
|Platforms  |PC, Web                                  |
|Post-launch|PSP homebrew port planned                |

This Python prototype serves as the **reference implementation**. The GDScript version will be verified against it during development.

-----

## Project

|         |                                        |
|---------|----------------------------------------|
|Studio   |Purify Games                            |
|Status   |Combat engine prototype — pre-production|
|Prototype|Python 3                                |
|Full game|Godot 4                                 |
|Genre    |Turn-based tactics RPG                  |

-----

> *This repository contains only the combat engine. Game assets, world design, and full source will not be public until a later stage of development.*
