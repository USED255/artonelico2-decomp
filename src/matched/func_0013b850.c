__asm__(
  ".set noreorder\n"
  ".globl func_0013b850\n"
  "func_0013b850:\n"
  "addiu $14,$4,16\n"
  "addiu $15,$4,96\n"
  "lq $6,0($15)\n"
  "sq $6,0($14)\n"
  "jr $31\n"
  "sw $0,4($4)\n"
  ".set reorder\n");
