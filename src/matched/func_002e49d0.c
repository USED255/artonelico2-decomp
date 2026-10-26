struct S { char pad[0x48]; int f48; };
extern int LibcString_8(void *, int, int);
extern void func_002fd820(int, void *);
void func_002e49d0(struct S *p, void *b){ if (!p->f48) LibcString_8(b, 0, 0xA8); else func_002fd820(p->f48, b); }
