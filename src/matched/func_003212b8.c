extern void eekernel_54(void *, void *);
extern void eekernel_57(void *);
void func_003212b8(char *p){ char buf[0x30]; if (p == 0) return; eekernel_54(p, buf); if (*(int *)buf == 4 || *(int *)buf == 0xC) eekernel_57(p); }
