/* baseelf_19 @ 0x001e0f60 (12 B) : lui $t7,%hi(D_007AF2D0) ; jr $ra ; lw $v0,%lo(...)($t7) */
/* The body is one global load through $t7; the symbol comes from config/symbol_addrs.txt. */
#include "externs.h"

int baseelf_19(void) { return D_007AF2D0; }
