extern char D_00BC6790[];
extern void func_001c798c(void *, int, int);
struct S { char pad[0x2078]; char *p[0x80]; };
void func_001b4314(int a, int b){ int i; for (i = 0; i < 0x80; i++) { char *p = ((struct S *)D_00BC6790)->p[i]; if (p) func_001c798c(p, a, b); } }
