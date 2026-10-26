struct S { char pad[4]; };
extern char D_009CF688[];
extern int func_002e4b58(struct S *);
extern void func_002e90c8(void *);
extern void func_002e4a08(struct S *, void *);
int func_002e4860(struct S *p){ char buf[0x40]; int r = func_002e4b58(p); if (r != 1) { func_002e90c8(D_009CF688); return -1; } func_002e4a08(p, buf); return *(int *)(buf + 0x24); }
