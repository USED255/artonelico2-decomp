# Does this handbook transfer to the 2.96 compiler?

[简体中文](CROSS-2.96.zh-CN.md) · [Handbook index](README.md) · [Laws](LAWS.md) · [Pass map](PASSES.md)

This project uses **two** compilers: `ee-gcc 3.2-ee-040921` for the game code and `ee-gcc 2.96-ee-001003-1`
for the CRI middleware. The handbook's rules were measured on 3.2, so the question "may I apply this to a
CRI function?" has a per-rule answer. Everything below was re-run on 2.96 with the same fixtures and flags
(`-O2 -G0`), reading the **object code** — 2.96's assembly prints `li.s`, a pseudo-instruction, which
misleads.

## What transfers

| Rule | On 2.96 |
| --- | --- |
| Narrow-compare idioms: `andi` for a narrow unsigned type, `sll`+`sra` for a narrow signed one ([L-EE-013](LAWS.md#l-ee-013--signedness-picks-slt-vs-sltu-a-narrower-type-adds-andi-or-sllsra-xori-marks-equality)) | ✅ same |
| Switch threshold: 6 dense cases become a table, 4 cases and sparse ranges stay a branch chain ([L-EE-010](LAWS.md#l-ee-010--a-switch-becomes-a-jump-table-only-when-count--5-and-range--10--count)) | ✅ same |
| `-G0`: a global is addressed absolutely with `lui %hi` / `%lo` ([L-EE-014](LAWS.md#l-ee-014--small-data-addressing-follows--g)) | ✅ same |
| Double constants: `move` for 0.0, `li`+`dsll32` when the low 32 bits are zero, otherwise the pool ([L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero)) | ✅ same |
| Frame composition and the save-slot count | ✅ same shape (not re-calibrated per value) |

## What does not

**Float constants.** [L-EE-011](LAWS.md#l-ee-011--float-constants-come-from-the-pool-a-double-is-inline-when-its-low-32-bits-are-zero)
says a non-zero float comes from the constant pool. That is true on **3.2** and false on **2.96**:

| `float f(void) { return V; }` | 3.2 | 2.96 |
| --- | --- | --- |
| `0.0f` | `mtc1` (zero register) | `mtc1` |
| `0.5f`, `1.0f`, `2.5f`, `-1.0f`, `100.0f` | `lui addiu lwc1` (**pool**) | `lui mtc1` (**inline**; the low 16 bits are zero) |
| `0.01f`, `3.14f`, `123.456f`, `1e30f` | **pool** | `lui ori mtc1` (**inline**) |

So on 2.96 a float is **always** materialised inline, and its low 16 bits only decide whether an `ori` is
needed — [L-EE-019](LAWS.md#l-ee-019--the-float-rule-is-version-specific-296-inlines-32-uses-the-pool). Before
respelling a float constant, check which compiler builds that source.

## Reproducing

`tools/compiler/ee-gcc-observe.py` takes any compiler and its fixtures assert **3.2** behaviour, so running
them against 2.96 is itself the demonstration:

```sh
python3 tools/compiler/ee-gcc-observe.py --cc ~/eecc/ee-gcc2.96/bin/ee-gcc --selftest
# float-pool fails on 2.96: the value is materialised inline instead
```

For the object-level comparison, compile both and disassemble:

```sh
for cc in ~/eecc/ee-gcc3.2-040921/bin/ee-gcc ~/eecc/ee-gcc2.96/bin/ee-gcc; do
  "$cc" -O2 -G0 -c -o /tmp/x.o - <<<'float f(void){return 0.5f;}'   # then disassemble
done
```

## Scope

Both compilers, `-O2 -G0`, synthetic fixtures. The 2.96 rows are `T3` (behaviour only): neither backend's
source is available and no binary anchor identifies the decision site.
