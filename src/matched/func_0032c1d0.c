struct S { char pad[0xC]; int f; char pad2[0x18]; };
extern int LibcString_8(void *, int, int);
void func_0032c1d0(struct S *p){ p->f = 0; LibcString_8((char *)p + 0x28, 0, 8); }
