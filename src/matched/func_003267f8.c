extern void LibcStdio_46(void *, void *, int, int);
extern void func_0031de90(void *, int);
extern char D_009D2F18[];
void func_003267f8(int a, unsigned int b, int c){ char buf[0x20]; LibcStdio_46(buf, D_009D2F18, a, (b + 0x7FF) >> 11); func_0031de90(buf, c); }
