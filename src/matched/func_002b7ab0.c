__asm__(
  ".set noreorder\n"
  ".globl func_002b7ab0\n"
  "func_002b7ab0:\n"
  "cfc2 $2,$vi28\n"
  "ori $2,$2,0x2\n"
  "ctc2 $2,$vi28\n"
  "jr $31\n"
  "nop\n"
  ".set reorder\n");
