/* baseelf_36 @ 0x0011a9bc (24 B) : addiu $t0,$zero,0xff 后尾调用 func_0011a93c（第 5 个参数走 $t0） */
#include "externs.h"

void baseelf_36(int a, int b, int c, int d) { func_0011a93c(a, b, c, d, 0xff); }
