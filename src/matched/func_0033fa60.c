void func_0033fa60(unsigned char *p, unsigned int len){ unsigned int i; for (i = 8; i < len; i += 2) { unsigned char a = p[i]; unsigned char b = p[i + 1]; p[i + 1] = a; p[i] = b; } }
