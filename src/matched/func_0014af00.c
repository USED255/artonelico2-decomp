extern void func_0014af78(int);
extern char D_005871E8[], D_009E3F80[];
int D_009DC030 __attribute__((section(".sdata"), weak));
void func_0014af00(void){ int idx = D_009DC030; char *base = D_005871E8; char *q; int v; if (idx < 0) return; q = (char *)(idx * 0x1C + (int)base); v = *(int *)(q + 8); v = *(int *)(v * 4 + (int)D_009E3F80); if (v == 0 || v == 2) return; { int i; for (i = 0; i < 4; i++) func_0014af78(i); } }
