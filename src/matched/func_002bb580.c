void func_002bb580(int **pp, unsigned a, long long b){ int *q = *pp; *(long long *)q = b; q += 2; *(long long *)q = a; q += 2; *pp = q; }
