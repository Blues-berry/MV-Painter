import csv, random
from collections import defaultdict
rows = list(csv.DictReader(open('/4T/CXY/MV-Painter/用户实验原始结果.CSV', encoding='utf-8-sig')))
print('cols:', list(rows[0].keys()))
for r in rows[:3]:
    print(r)
votes = defaultdict(dict)
for r in rows:
    p = (r['participant'] or '').strip()
    o = (r['object'] or '').strip()
    c = (r['criterion'] or '').strip().lower()
    ch = (r['choice'] or '').strip()
    if not p or not o:
        print('EMPTY FIELD:', r)
        continue
    votes[p].setdefault(o, {})[c] = ch
P = sorted(votes)
O = sorted({o for v in votes.values() for o in v})
print('participants:', len(P), 'objects:', len(O))
crits = ['texture', 'shape', 'overall']; meths = ['s1.25', 's2.50', 'C3']
random.seed(42); N = 10000
res = {c: {m: [] for m in meths} for c in crits}
diff = {('overall', 'C3', 's1.25'): [], ('overall', 'C3', 's2.50'): [], ('texture', 's1.25', 'C3'): []}
for _ in range(N):
    Ps = [random.choice(P) for _ in P]
    tally = {c: {m: 0 for m in meths} for c in crits}; tot = 0
    for p in Ps:
        objs = list(votes[p].keys())
        for o in [random.choice(objs) for _ in objs]:
            for c in crits:
                ch = votes[p][o].get(c)
                if ch in meths:
                    tally[c][ch] += 1; tot += 1
    for c in crits:
        for m in meths: res[c][m].append(tally[c][m] / max(tot, 1))
    for (c, a, b2) in diff: diff[(c, a, b2)].append((tally[c][a] - tally[c][b2]) / max(tot, 1))
def ci(v):
    v = sorted(v); return v[int(.025 * N)], v[int(.975 * N)]
for c in crits:
    for m in meths:
        lo, hi = ci(res[c][m])
        print('%s %s: mean %.1f%%, 95%%CI [%.1f%%, %.1f%%]' % (c, m, 100 * sum(res[c][m]) / N, 100 * lo, 100 * hi))
for (c, a, b2), v in diff.items():
    lo, hi = ci(v)
    print('%s %s-%s: mean %.1f%%, 95%%CI [%.1f%%, %.1f%%]' % (c, a, b2, 100 * sum(v) / N, 100 * lo, 100 * hi))
