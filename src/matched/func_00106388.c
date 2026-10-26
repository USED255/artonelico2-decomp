extern void eepatch_4(void);
extern void eepatch_5(void);
extern int D_009E2760[];
int D_009DB7A8 __attribute__((section(".sdata")));
void func_00106388(int v){ eepatch_4(); D_009E2760[D_009DB7A8] = v; D_009DB7A8 = D_009DB7A8 + 1; eepatch_5(); }
