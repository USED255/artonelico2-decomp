extern char D_009D0528[];
extern void LibcStdio_46(char *, void *, int, int);
extern void func_002e7838(int, char *);
void func_002e7f78(int x, int a, int b){ char buf[0x20]; LibcStdio_46(buf, D_009D0528, a, (unsigned)(b + 0x7FF) >> 11); func_002e7838(x, buf); }
