extern char D_007D4490[];
__asm__(
  ".set noreorder\n"
  ".globl baseelf_61\n"
  "baseelf_61:\n"
  "sll $5,$5,0x4\n"
  "lui $15, %hi(D_007D4490)\n"
  "addiu $15,$15, %lo(D_007D4490)\n"
  "addu $5,$5,$15\n"
  "lq $8,0($5)\n"
  "sq $8,0($4)\n"
  "jr $31\n"
  "nop\n"
  ".set reorder\n");
