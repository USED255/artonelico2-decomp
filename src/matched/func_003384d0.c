extern void func_00338798(void);
extern void func_003383a0(void *);
void func_003384d0(char *p){ if (!p) return; func_00338798(); if (*(signed char *)p == 1) { *(char *)p = 0; func_003383a0(p); } }
