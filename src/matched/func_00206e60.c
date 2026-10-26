extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
extern int func_00208d68(int, int);
extern int func_00208e2c(int);
void func_00206e60(char *pa, char *pb, int c, int d, int e, int f, int g, int h){ char buf[0x10]; int t; func_0021b834(buf); __asm__ volatile("slt $14,$0,%0\n\taddiu $15,$0,1\n\tmovz %0,$15,$14" : "+r"(c) : : "$14", "$15"); c = c + func_00208d68((int)pb, c); buf[8] = 0; *(int *)buf = -c; *(short *)(buf + 4) = h * 10 - 10; *(short *)(buf + 6) = d; buf[9] = func_00208e2c(e); func_0021be98(pa, pb, buf); if (g) { func_0021b834(buf); buf[8] = 8; func_0021be98(pa, pb, buf); } }
