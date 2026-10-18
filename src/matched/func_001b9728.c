__asm__(
  ".set noreorder\n"
  ".globl func_001b9728\n"
  "func_001b9728:\n"
  "addiu $4,$4,112\n"
  "lq $8,0($5)\n"
  "sq $8,0($4)\n"
  "jr $31\n"
  "nop\n"
  ".set reorder\n");
