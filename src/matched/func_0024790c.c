extern char D_007EADA8[];
extern void func_00247870(char *, int *, int *);
extern void func_0018f024(int, int);
void func_0024790c(int i){ int a = -1, b = -1; char *base = D_007EADA8; char *q = (char *)(i * 0x16 + (int)base); func_00247870(q + 6, &a, &b); func_0018f024(a, b); }
