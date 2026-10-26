extern void *func_001e5dd0(int *);
extern int func_001e36c0(void *);
int func_001e37fc(void){ int slot = 0; void *p; for (;;) { p = func_001e5dd0(&slot); if (!p) return 0; if (func_001e36c0(p)) return 1; } }
