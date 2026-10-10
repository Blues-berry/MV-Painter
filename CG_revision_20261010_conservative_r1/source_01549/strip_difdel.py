#!/usr/bin/env python3
"""Strip latexdiff DELETED content from a marked tex, keeping additions-only markup.
Body-only processing (preamble definitions untouched). Brace-balance aware."""
import re, sys

SRC = 'final_0903_marked.tex'
DST = 'final_0903_marked_addonly.tex'
src = open(SRC, encoding='utf-8').read()
i = src.index(r'\begin{document}')
head, body = src[:i], src[i:]

TOKENS = [r'\DIFdelbeginFL', r'\DIFdelendFL', r'\DIFdelbegin', r'\DIFdelend',
          r'\DIFmodbegin', r'\DIFmodend']
out = []
n = len(body)
k = 0
debt = 0
removed_del = 0
while k < n:
    # pure DIF comment lines -> drop entirely
    if body.startswith('%DIFDELCMD', k) or body.startswith('%DIFAUXCMD', k):
        j = body.find('\n', k)
        k = n if j == -1 else j + 1
        continue
    # latexdiff group opener { followed by DIFAUXCMD comment -> drop line, owe one }
    if body[k] == '{' and body.startswith('%DIFAUXCMD', k + 1):
        debt += 1
        j = body.find('\n', k)
        k = n if j == -1 else j + 1
        continue
    matched = False
    for tok in TOKENS:
        if body.startswith(tok, k):
            k += len(tok)
            matched = True
            break
    if matched:
        continue
    if body.startswith(r'\DIFdelFL{', k) or body.startswith(r'\DIFdel{', k):
        tok = r'\DIFdelFL' if body.startswith(r'\DIFdelFL', k) else r'\DIFdel'
        j = k + len(tok)
        assert body[j] == '{', f'no brace after {tok} at offset {k}'
        depth = 0
        while j < n:
            c = body[j]
            if c == '\\':
                j += 2
                continue
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        assert depth == 0, f'unbalanced DIFdel group at offset {k}'
        k = j + 1
        removed_del += 1
        continue
    if body[k] == '}' and debt == 1:
        debt = 0
        k += 1
        continue
    out.append(body[k])
    k += 1
assert debt == 0, 'unclosed DIFAUXCMD brace group'
res = ''.join(out)

# truncate any mid-line DIF comments (safe: they are comments)
lines = []
for ln in res.split('\n'):
    for marker in ('%DIFDELCMD', '%DIFAUXCMD'):
        p = ln.find(marker)
        if p > 0 and ln[p - 1] != '\\':
            ln = ln[:p]
    lines.append(ln)
res = '\n'.join(lines)

open(DST, 'w', encoding='utf-8').write(head + res)
print(f'DIFdel groups removed: {removed_del}')
print('body brace balance:', res.count('{') - res.count('}'))
