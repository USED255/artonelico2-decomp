__asm__(
  ".set noreorder\n"
  ".globl func_001ed1cc\n"
  "func_001ed1cc:\n"
  "addiu $15,$4,16\n"
  "lq $8,0($5)\n"
  "sq $8,0($15)\n"
  "addiu $4,$4,32\n"
  "lq $8,0($15)\n"
  "sq $8,0($4)\n"
  "jr $31\n"
  "nop\n"
  ".set reorder\n");
