extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
extern int func_001eb354(void *, int);
extern void *baseelf_191(int);
extern int LibcStdlib_34(void);
extern void func_002089a8(void *, void *, int);
void func_0020696c(char *a, char *b, int c, int d, int e){ char buf[0x10]; int n; void *p; n = c + func_001eb354(a, 0x11); n = n - func_001eb354(b, 0x11); n += 0x23; n = n < 0 ? 0 : (n < 0x65 ? n : 0x64); if (*(short *)(b + 0x1A) == 1) { p = baseelf_191(*(short *)(b + 0x1E)); if (*(short *)((char *)p + 8) >= 0x63) n = 0; } { int v = LibcStdlib_34(); v >>= 8; if (v % 100 < n) { func_0021b834(buf); buf[8] = 0x10; *(short *)(buf + 4) = d; func_0021be98(a, b, buf); } else if (e) func_002089a8(a, b, 1); } }