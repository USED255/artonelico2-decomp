extern void *func_001e5dd0(int *);
extern void baseelf_84(void *);
void func_001f9d34(void){ int slot = 0; void *p; for (;;) { p = func_001e5dd0(&slot); if (!p) break; baseelf_84(p); } }
