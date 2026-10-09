"""Styles module for offline NPC training."""
import random
from .common import BOUNDS, clamp

def make_profiles(priors, seed):
    rng = random.Random(seed)
    # Independent shuffled strata prevent identical drivers and correlated personalities.
    strata = {key: list(range(19)) for key in BOUNDS}
    for order in strata.values():
        rng.shuffle(order)
    spread = {'aggression': .30, 'corner_skill': .026, 'preferred_lane_cm': 240, 'decision_seconds': 1.4}
    profiles = []
    for index in range(19):
        profile = {'racer_index': index + 1}
        for key, (lo, hi) in BOUNDS.items():
            # Limit the centre so all strata survive clamping and remain distinct.
            width = spread[key]
            centre = clamp(priors[key], lo + width / 2, hi - width / 2)
            unit = (strata[key][index] + rng.uniform(.15, .85)) / 19 - .5
            profile[key] = round(clamp(centre + unit * width, lo, hi), 6)
        profiles.append(profile)
    return profiles
