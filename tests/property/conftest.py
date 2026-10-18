from hypothesis import settings

# Derandomized so every run replays the same generated examples (seeded replay).
settings.register_profile("deterministic", derandomize=True, max_examples=200, deadline=None)
settings.load_profile("deterministic")
