__asm__(
  ".set noreorder\n"
  ".globl func_00158808\n"
  "func_00158808:\n"
  "addiu $29,$29,-16\n"
  "sd $31,0($29)\n"
  "lq $8,0($5)\n"
  "sq $8,0($4)\n"
  "swc1 $f12,32($4)\n"
  "move $5,$6\n"
  "ld $31,0($29)\n"
  "j func_0015882c\n"
  "addiu $29,$29,16\n"
  ".set reorder\n");
