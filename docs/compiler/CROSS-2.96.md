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
| Frame composition and the save-slot count ([L-EE-012](LAWS.md#l-ee-012--frame-composition-varsoutgoing-args8-b-per-saved-register-saturating-at-10-saved-registers)) | ✅ **identical**, re-calibrated per value: k = 2/4/6/8/10/12/16/20 gives frame 32/48/64/80/96/96/112/128 with regs 4/6/8/10/10/10/10/10 |
| 64-bit integer arithmetic is inline: `daddu`/`dsubu`/`dsll`/`dsra`; 64-bit multiply and divide call libgcc ([L-EE-043](LAWS.md#l-ee-043--64-bit-integers-are-native-only-multiply-divide-and-modulo-call-out)) | ✅ same |
| `float` lives in COP1 and `double` in general registers ([L-EE-042](LAWS.md#l-ee-042--float-lives-in-cop1-double-lives-in-general-registers)) | ✅ same |
| Loop back edges use the branch-likely form ([L-EE-045](LAWS.md#l-ee-045--loop-back-edges-are-branch-likely-forward-branches-are-not)) | ✅ same |
| A tail call is a `j` to the target ([L-EE-036](LAWS.md#l-ee-036--tail-calls-are-jumps--but-not-below--o2)) | ✅ same |
| The equality idiom `xor` + `sltu …,1` ([L-EE-040](LAWS.md#l-ee-040--comparison-idioms-materialised-as-values-branched-as-conditions)) | ✅ same |
| `sqrtf` is inlined as `sqrt.s` ([L-EE-051](LAWS.md#l-ee-051--zero-comparisons-float-branches-and-an-inlined-sqrtf)) | ✅ same |
| A 128-bit container is moved with `lq`/`sq` ([L-EE-041](LAWS.md#l-ee-041--128-bit-containers-lqsq-a-register-pair-and-no-by-value-return)) | ✅ same shape; 2.96 picks a different register |
| Default function alignment is 8 bytes ([L-EE-022](LAWS.md#l-ee-022--function-alignment-8-bytes-by-default-4-with--falign-functions4)) | ✅ same `2**3` |

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

**The COP1 accumulator.** On 3.2 an expression that sums two or more products uses the COP1 accumulator
([L-EE-050](LAWS.md#l-ee-050--the-cop1-accumulator-a-sum-of-products-uses-mulasmadds)); on 2.96 the same expression is plain multiplies and an add:

| `float f(float a,float b,float c,float d){ return a*b + c*d; }` | code |
| --- | --- |
| 3.2 | `mula.s $f12,$f13` + `madd.s $f0,$f14,$f15` |
| 2.96 | `mul.s` + `mul.s` + `add.s` — **no accumulator** |

**A 16-byte structure copy.** 3.2 unrolls 32-bit pairs; 2.96 moves 64-bit halves with unaligned pairs:

| `struct S{int a,b,c,d;}; void f(struct S *d, struct S *s){ *d = *s; }` | code |
| --- | --- |
| 3.2 | `lw`/`sw` runs ([L-EE-038](LAWS.md#l-ee-038--aggregate-copies-unrolled-to-32-bytes-then-an-inline-ldlldr-loop--never-memcpy)) |
| 2.96 | **`ldl`/`ldr` + `sdl`/`sdr`** pairs |

**Vector types do not exist on 2.96.** `mode(V4SI)` and `mode(V4SF)` are rejected outright (`no data type`),
so every 128-bit rule ([L-EE-041](LAWS.md#l-ee-041--128-bit-containers-lqsq-a-register-pair-and-no-by-value-return)) and the whole COP2/VU0 argument
([L-EE-048](LAWS.md#l-ee-048--cop2vu0-instructions-cannot-come-from-c)) is a 3.2-only matter.

### Two fingerprints worth remembering

Both compilers build code for this project — 3.2 for the game, 2.96 for the CRI middleware — so these shapes
tell you which one produced a function:

* `mula.s`/`madd.s`/`msub.s` in the instruction stream ⇒ **3.2** (2.96 never emits the accumulator);
* a 16-byte copy as `ldl`/`ldr` pairs ⇒ **2.96** (3.2 uses `lw`/`sw` at that size);
* `mode(V4SI)`/`mode(V4SF)` source that compiles at all ⇒ **3.2**.

**The ABI is not one of the differences.** An early look at the 9th argument suggested otherwise — but that was a
measurement artefact (3.2 materialises the incoming stack address with `addu $15,$sp,0` before loading, which
looks different from 2.96's direct `lw`). Checked properly, the stack layout is identical on both, so every
convention in [ABI](ABI.md) can be used for middleware and game code alike.

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
