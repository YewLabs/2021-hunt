# NPC activity is governed by a d6 check against their cooldown. If the d6 is
# less than or equal to the cooldown, the NPC acts; otherwise, the cooldown
# gets incremented. When a counting session starts, each NPC's cooldown is set
# to its INITIAL cooldown; after it acts, it is set to its RESET cooldown.

# Note there is also extended behavior for solvers that hit 100+; for each full
# hundred the solvers have successfully counted, the RESET cooldown is
# decreased in magnitude to a minimum of half its original value. For example,
# the monkey's (firefly's) reset cooldown at count 250 is -12, and will reach
# its "minimum" of -7 at count 700.

NPC_INITIAL_COOLDOWNS = {
    'monkey': -2,
    'robot': -14,
    'owl': -6,
    'human': -30,
    'creodont': -4,
}

NPC_RESET_COOLDOWNS = {
    'monkey': -14,
    'robot': -48,
    'owl': -11,
    'human': -12,
    'creodont': -35,
}

def reset_cooldown(npc_name, count):
  """Compute an NPC's reset cooldown, with an adjustment for high-count teams."""
  return min(
      NPC_RESET_COOLDOWNS[npc_name] + int(count / 100),
      int(NPC_RESET_COOLDOWNS[npc_name] / 2))
