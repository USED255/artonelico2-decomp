__asm__(
  ".set noreorder\n"
  ".globl func_001f3580\n"
  "func_001f3580:\n"
  "lq $8,0($5)\n"
  "sq $8,0($4)\n"
  "sh $6,22($4)\n"
  "sh $7,20($4)\n"
  "ld $15,24($4)\n"
  "lui $14,0x1\n"
  "or $15,$15,$14\n"
  "jr $31\n"
  "sd $15,24($4)\n"
  ".set reorder\n");
