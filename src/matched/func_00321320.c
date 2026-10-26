extern void eekernel_54(void *, void *);
extern int eekernel_63(void *);
int func_00321320(char *p){ char st[0x30]; int r = 0; if (p != 0) { eekernel_54(p, st); if (*(int *)st == 8 || *(int *)st == 0xC) { r = eekernel_63(p); } } return r; }
