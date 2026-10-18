__asm__(
  ".set noreorder\n"
  ".globl func_0029eeec\n"
  "func_0029eeec:\n"
  "addiu $15,$4,16\n"
  "addiu $4,$4,32\n"
  "lq $6,0($15)\n"
  "sq $6,0($4)\n"
  "jr $31\n"
  "nop\n"
  ".set reorder\n");
