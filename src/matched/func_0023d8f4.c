/* func_0023d8f4 @ 0x0023d8f4 (16 B) : store a sign-extended byte at D_009DFD0C
 *
 * D_009DFD0C is small data: the weak definition in .sdata makes ee-gcc emit the
 * %gp_rel form. The linker discards it, because the original asm object keeps the
 * strong definition (see obj_gate P2a).
 */
__attribute__((weak, section(".sdata"))) signed char D_009DFD0C;

void func_0023d8f4(signed char v)
{
  D_009DFD0C = v;
}
