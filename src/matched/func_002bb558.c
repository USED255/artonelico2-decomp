void func_002bb558(int **p, long long v){ int *q = *p; q[0] = (int)v; q = q + 1; q[0] = (int)(v >> 32); p[0] = q + 1; }
