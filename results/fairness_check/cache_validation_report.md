# Cache Validation Report (Minimal Check, Public Copy)

- Scope: IEEE69 + DE
- Design: cache off 2 runs + cache on 2 runs (same seeds)
- Seeds: [868077494, 1800860156]
- Budget: 1240
- Threshold: abs diff < 0.0001

## Per-seed comparison

| seed | final_fitness (off) | final_fitness (on) | abs diff | pass |
|---:|---:|---:|---:|:---:|
| 868077494 | 0.529200867178 | 0.529200867178 | 0.000000000000 | ✅ |
| 1800860156 | 0.523226346816 | 0.523226346816 | 0.000000000000 | ✅ |

## Conclusion

- max abs diff (final_fitness): 0.000000000000
- pass (< 0.0001): True
- Result: cache on/off consistency passed for minimal verification.

