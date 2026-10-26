extern int D_00AD7FF0[];
extern char D_009DFC70[];
void func_00112924(int a, int b, int c){ long long v; D_00AD7FF0[0] = a; D_00AD7FF0[1] = b; D_00AD7FF0[2] = c; v = (long long)a | ((long long)D_00AD7FF0[3] << 24); v |= ((long long)c << 16) | ((long long)b << 8); *(long long *)D_009DFC70 = v; }
