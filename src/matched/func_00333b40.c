extern char D_009D5250[];
extern void func_00333990(void);
extern int fileio_9(int, int, int);
extern void eetty_5(void *, int);
extern void func_003339c8(void);
int func_00333b40(int a, int b, int c){ int r; func_00333990(); r = fileio_9(a, b, c); if (r < 0) eetty_5(D_009D5250, r); func_003339c8(); return r; }
