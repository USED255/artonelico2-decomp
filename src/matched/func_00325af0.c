extern void func_00325308(void *);
void func_00325af0(char *p){ if (*(signed char *)(p + 1) != 2) return; if ((*(long long *)(p + 0x48) & ((0xFF00LL << 32) | 0xFF00)) != (0x8000LL << 25)) return; func_00325308(p); }
