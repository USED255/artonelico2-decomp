extern char D_009CF420[];
extern void LibcStdio_46(char *, void *, int, int);
extern void func_002e3528(int, char *);
void func_002e3dd8(int x, int a, int b){ char buf[0x20]; LibcStdio_46(buf, D_009CF420, a, (unsigned)(b + 0x7FF) >> 11); func_002e3528(x, buf); }
