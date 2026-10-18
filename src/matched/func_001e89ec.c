__asm__(
  ".set noreorder\n"
  ".globl func_001e89ec\n"
  "func_001e89ec:\n"
  "addiu $29,$29,-16\n"
  "lw $15,2848($4)\n"
  "addiu $15,$15,16\n"
  "lq $8,0($15)\n"
  "sq $8,0($29)\n"
  "lwc1 $f0,0($29)\n"
  "jr $31\n"
  "addiu $29,$29,16\n"
  ".set reorder\n");
