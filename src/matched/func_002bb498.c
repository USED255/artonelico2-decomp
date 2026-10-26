__asm__(
  ".set noreorder\n"
  ".globl func_002bb498\n"
  "func_002bb498:\n"
  "lw $2,0($4)\n"
  "addiu $3,$2,16\n"
  "sq $5,0($2)\n"
  "sw $3,0($4)\n"
  "jr $31\n"
  "sw $2,12($4)\n"
  ".set reorder\n");
