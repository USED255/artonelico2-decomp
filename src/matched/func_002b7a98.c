__asm__(
  ".set noreorder\n"
  ".globl func_002b7a98\n"
  "func_002b7a98:\n"
  "cfc2 $2,$vi29\n"
  "andi $2,$2,0xf\n"
  "xori $2,$2,0x1\n"
  "jr $31\n"
  "sltiu $2,$2,1\n"
  ".set reorder\n");
