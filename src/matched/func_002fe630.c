struct S { char pad[4]; };
extern int func_002fe868(struct S *);
int func_002fe630(struct S *p, int *a, int *b){ if (func_002fe868(p)) { *a = -2; *b = 1; return 0; } return 0; }
