extern void eekernel_55(void *, void *);
extern void eepatch_21(void *);
void func_00321268(char *p){ char buf[0x30]; if (p == 0) return; eekernel_55(p, buf); if (*(int *)buf == 4 || *(int *)buf == 0xC) eepatch_21(p); }
