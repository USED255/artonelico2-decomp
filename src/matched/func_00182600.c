extern char D_009DFCD4[];
__asm__(
  ".set noreorder\n"
  ".globl func_00182600\n"
  "func_00182600:\n"
  "lui $12, %hi(D_009DFCD4)\n"
  "lui $15,0x1\n"
  "lw $14, %lo(D_009DFCD4)($12)\n"
  "ori $15,$15,0x8000\n"
  "lui $13,0x1\n"
  "addu $14,$14,$15\n"
  "ori $13,$13,0xbd40\n"
  "sb $0,15696($14)\n"
  "lw $15, %lo(D_009DFCD4)($12)\n"
  "addu $15,$15,$13\n"
  "sq $0,0($15)\n"
  "jr $31\n"
  "nop\n"
  ".set reorder\n");
