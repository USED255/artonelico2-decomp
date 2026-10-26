__asm__(
  ".set noreorder\n"
  ".globl func_00266a48\n"
  "func_00266a48:\n"
  "sw $5,0($4)\n"
  "addiu $15,$4,16\n"
  ".word 0x11000004\n"
  "sw $8,4($4)\n"
  "sh $6,8($4)\n"
  "lq $8,0($7)\n"
  "sq $8,0($15)\n"
  "jr $31\n"
  "nop\n"
  ".set reorder\n");
