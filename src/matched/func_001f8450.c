extern char D_007D44D0[];
__asm__(
  ".set noreorder\n"
  ".globl func_001f8450\n"
  "func_001f8450:\n"
  "sll $5,$5,0x4\n"
  "lui $15, %hi(D_007D44D0)\n"
  "addiu $15,$15, %lo(D_007D44D0)\n"
  "addu $5,$5,$15\n"
  "lq $8,0($5)\n"
  "sq $8,0($4)\n"
  "jr $31\n"
  "nop\n"
  ".set reorder\n");
