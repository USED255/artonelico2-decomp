extern int func_002fd698(void *, int);
extern void func_002fe118(void *, void *, int *, int *);
int func_002fe1e0(char *p){ int a, b, s; if (!func_002fd698(p, 6)) return 0; s = func_002fd698(p, 0x33); if (!s) return 0; func_002fe118(p, p + 0xD88, &a, &b); return s < (a / b); }
