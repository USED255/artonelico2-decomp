extern char D_00BB8018[];
__asm__(
  ".set noreorder\n"
  ".globl func_0016d270\n"
  "func_0016d270:\n"
  "addiu $29,$29,-16\n"
  "lui $15, %hi(D_00BB8018)\n"
  "sd $31,0($29)\n"
  "addiu $15,$15, %lo(D_00BB8018)\n"
  "sll $5,$5,0x2\n"
  "addu $5,$5,$15\n"
  "move $15,$6\n"
  "lw $5,0($5)\n"
  "lq $6,0($15)\n"
  "sq $6,0($5)\n"
  "ld $31,0($29)\n"
  "j func_0016c8b8\n"
  "addiu $29,$29,16\n"
  ".set reorder\n");
