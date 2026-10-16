/* EE kernel syscall stub (SDK hand-written assembly).
 *
 * This symbol has **no recoverable C source**: the original PlayStation 2 runtime library
 * ships this entry point as hand-written assembly (the disassembly header itself says
 * "Handwritten function"), and the `syscall` instruction cannot be produced by any C
 * expression - only by inline assembly. The body below is therefore a **verbatim
 * transcription** of the target instructions; the epilogue (`jr $31; nop`) is emitted by
 * the compiler.
 *
 * Same approach as other PS2 matching decompilations (e.g. ethteck/kh1 uses
 * `#define SYSCALL(id) __asm__ volatile("li $3,"#id"\n syscall")`); Sony's own
 * `eekernel.h` likewise uses `__asm__ volatile(...)` for its primitives.
 *
 * objdiff 100.0 with the equal-length guard (P-97), level: -Os.
 * NOT a semantic decompilation - see docs/knowledge-base/reports/R37-syscall-stub-landing.md
 * in the research repository for the full symbol list and the inclusion criterion. */
void sceSifSetDma(void) {
    __asm__ volatile ("addiu $3, $0, 0x77");
    __asm__ volatile ("syscall 0");
}
