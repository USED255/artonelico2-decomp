/* baseelf_15 @ 0x001f5d20 (8 B) : jr $ra ; lh $v0,0x18($a0) */
#include "externs.h"

short baseelf_15(char *p) { return *(short *)(p + 24); }
