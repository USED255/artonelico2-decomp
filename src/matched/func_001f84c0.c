extern char D_007D4550[];
__asm__(
  ".set noreorder\n"
  ".globl func_001f84c0\n"
  "func_001f84c0:\n"
  "lui $15, %hi(D_007D4550)\n"
  "addiu $15,$15, %lo(D_007D4550)\n"
  "lq $8,0($15)\n"
  "sq $8,0($4)\n"
  "jr $31\n"
  "nop\n"
  ".set reorder\n");
