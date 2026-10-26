extern volatile int D_008188D8[];
extern void *func_003060a8(void);
extern void func_003060f8(void *);
void *func_00306050(void){ char *p = func_003060a8(); if (p == 0) return p; func_003060f8(p); D_008188D8[0] = D_008188D8[0] + 1; *(int *)p = 1; return p; }
