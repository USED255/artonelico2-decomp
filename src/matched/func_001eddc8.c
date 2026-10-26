__asm__(
  ".set noreorder\n"
  ".globl func_001eddc8\n"
  "func_001eddc8:\n"
  "addiu $5,$5,2896\n"
  "lq $8,0($5)\n"
  "sq $8,0($4)\n"
  "andi $6,$6,0x2000\n"
  ".word 0x54c00001\n"
  "sw $0,4($4)\n"
  "jr $31\n"
  "nop\n"
  ".set reorder\n");
