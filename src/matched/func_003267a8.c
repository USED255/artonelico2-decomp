extern char D_009D2F18[];
extern void LibcStdio_46(char *, void *, int, int);
extern void func_00320730(int, char *);
void func_003267a8(int x, int a, int b){ char buf[0x20]; LibcStdio_46(buf, D_009D2F18, a, (unsigned)(b + 0x7FF) >> 11); func_00320730(x, buf); }
