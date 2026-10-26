struct S { char pad[4]; int f4; char pad2[0x588]; int f590; };
extern char D_009CF498[];
extern int func_002e4b58(struct S *);
extern void func_002e90c8(void *);
extern void func_002fba50(int);
extern void func_002e9f20(struct S *);
void func_002e3ee8(struct S *p){ int r = func_002e4b58(p); if (r != 1) { func_002e90c8(D_009CF498); return; } if (!p->f4) return; if (p->f590 == r) return; func_002fba50(*(int *)((char *)p + 0x48)); func_002e9f20(p); p->f590 = r; }
