extern void eepatch_4(void);
extern void eepatch_5(void);
extern int D_009E2778[];
int D_009DB7B0 __attribute__((section(".sdata")));
void func_00106408(int v){ eepatch_4(); D_009E2778[D_009DB7B0] = v; D_009DB7B0 = D_009DB7B0 + 1; eepatch_5(); }
