__asm__(
  ".set noreorder\n"
  ".globl func_0015f67c\n"
  "func_0015f67c:\n"
  "li $15,1\n"
  "sh $15,0($4)\n"
  "addiu $4,$4,32\n"
  "lq $8,0($5)\n"
  "sq $8,0($4)\n"
  "jr $31\n"
  "nop\n"
  ".set reorder\n");
