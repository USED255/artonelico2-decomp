extern char D_0096F1DC[];
__asm__(
  ".set noreorder\n"
  ".globl func_001f83cc\n"
  "func_001f83cc:\n"
  "addiu $5,$5,2896\n"
  "lq $8,0($5)\n"
  "sq $8,0($4)\n"
  "lui $15, %hi(D_0096F1DC)\n"
  "addiu $15,$15, %lo(D_0096F1DC)\n"
  "lwc1 $f0,0($15)\n"
  "jr $31\n"
  "swc1 $f0,0($4)\n"
  ".set reorder\n");
