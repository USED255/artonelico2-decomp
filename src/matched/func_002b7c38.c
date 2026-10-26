__asm__(
  ".set noreorder\n"
  ".globl func_002b7c38\n"
  "func_002b7c38:\n"
  "andi $4,$4,0xffff\n"
  "ctc2 $4,$vi27\n"
  "jr $31\n"
  "vcallmsr $vi27\n"
  ".set reorder\n");
