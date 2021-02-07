import os
import random


MY_DIR = os.path.dirname(__file__)
STYLES_PATH = os.path.join(MY_DIR, 'display_adjectives.txt')
BASES_PATH = os.path.join(MY_DIR, 'display_nouns.txt')
STYLES, BASES = [], []


def generate_animal_name():
  """Generates an animal name and an associated hash."""
  global STYLES, BASES
  if not STYLES:
    with open(STYLES_PATH, 'r') as s_file:
      STYLES = s_file.read().strip().split('\n')
  if not BASES:
    with open(BASES_PATH, 'r') as b_file:
      BASES = b_file.read().strip().split('\n')
  style_id = random.randint(0, len(STYLES) - 1)
  base_id = random.randint(0, len(BASES) - 1)
  return (f'{STYLES[style_id]} {BASES[base_id]}',
          (style_id * len(BASES) + base_id))
