struct S { char pad[0x170]; int f170; };
extern struct S D_00BFF280;
void func_002363d0(int a){ int v = D_00BFF280.f170 + a; if (v > 1000000000) v = 1000000000; D_00BFF280.f170 = v; }
