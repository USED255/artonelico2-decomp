extern int LibcString_16(void *);
extern void func_003198b0(void *, int, void *, void *, void *);
void func_0031a488(char *p, char *s){ char buf[6]; int n = LibcString_16(s); func_003198b0(s, n, buf, buf + 2, buf + 4); *(short *)(p + 0xA0) = *(unsigned short *)(buf); *(short *)(p + 0xA2) = *(unsigned short *)(buf + 2); *(short *)(p + 0xA4) = *(unsigned short *)(buf + 4); }
