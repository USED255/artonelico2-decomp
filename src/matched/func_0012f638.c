extern char D_00AD8310[];
extern char D_00583A70[];
extern void func_002b9b40(void *, void *, void *);
extern void func_002ba0b8(void *, void *, void *);
extern void func_002b9cc0(void *, void *);
void func_0012f638(void){ char a[0x10]; char b[0x10]; func_002b9b40(a, D_00AD8310, D_00583A70); func_002ba0b8(b, D_00AD8310 + 0xC0, D_00AD8310 + 0x110); func_002b9cc0(a, b); }
