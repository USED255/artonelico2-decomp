struct E { short a; char b; char pad[0x4D]; };
extern struct E D_00BFE220[];
void func_001e08e0(int i, int b, int c){ if (c == -1) return; D_00BFE220[i].a = c; D_00BFE220[i].b = b; }
