struct S { char pad[0x7D94]; short idx; };
struct E { short f0; short f2; short f4; char pad[0x18]; int f20; };
extern char D_007E8BE8[];
extern void func_0013f8dc(struct S *);
extern void func_001409d0(int, int, int, int, int, int, int);
void func_00240a68(struct S *p){ func_0013f8dc(p); struct E *e = (struct E *)(D_007E8BE8 + p->idx * 0x48); func_001409d0(e->f20, 0, e->f2, e->f4, e->f0, -1, 1); }
