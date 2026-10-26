extern char D_00BB8578[];
extern void func_0018dd88(int, int, int);
void func_0018dd48(int a, int b, int c){ char *e = D_00BB8578 + (a * 0x3C + b) * 2; e = e + 0x20; *(unsigned short *)(e + 4) = *(unsigned short *)(e + 4) + c; func_0018dd88(a, b, c); }
