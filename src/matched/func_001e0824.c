struct E { short a; char b; char pad[0x4D]; };
extern struct E D_00BFE540[];
void func_001e0824(int i, int b, int c){ if (c == -1) return; D_00BFE540[i].a = c; D_00BFE540[i].b = b; }
