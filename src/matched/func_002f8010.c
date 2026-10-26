extern void eepatch_4(void);
extern void eepatch_5(void);
void func_002f8010(int v){ eepatch_4(); *(volatile int *)0x1000F590 = *(volatile int *)0x1000F520 | 0x10000; *(volatile int *)0x1000B400 = v; *(volatile int *)0x1000F590 = *(volatile int *)0x1000F520 & 0xFFFEFFFF; eepatch_5(); }
