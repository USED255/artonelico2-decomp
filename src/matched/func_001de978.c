extern volatile int D_0079C91C[];
extern volatile char D_00BFD280[];
void func_001de978(int i, int v){ int p = *(int *)D_0079C91C; int idx = *(short *)(i * 0x14 + p); if (idx == -1) return; D_00BFD280[idx] = (char)v; }
