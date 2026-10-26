unsigned int D_009DE060 __attribute__((section(".sdata"), weak));
extern int func_001dcfbc(void);
int func_001dc284(void){ int r = 0; if (func_001dcfbc() == 1) { int t = *(short *)(D_009DE060 + 0x18) < 2; r = !t; } return r; }
