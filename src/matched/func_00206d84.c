extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
extern void *func_001e5dd0(int *);
extern int LibcStdlib_34(void);
extern void *baseelf_191(int);
void func_00206d84(char *a, int b, int c){ int slot = 0; char buf[0x10]; void *p; while (1) { p = func_001e5dd0(&slot); if (!p) break; if (*(short *)((char *)p + 0x1A) == 1) { p = baseelf_191(*(short *)((char *)p + 0x1E)); if (*(short *)((char *)p + 8) >= 0x63) return; } } { int v = LibcStdlib_34(); v >>= 8; if (v % 100 >= c) return; } func_0021b834(buf); buf[8] = 0x25; *(int *)buf = 1; *(short *)(buf + 4) = 1; func_0021be98(a, (void *)(long)b, buf); }
