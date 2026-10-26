struct S { char pad[0x49]; signed char b49; };
extern void func_00324c18(struct S *);
extern void func_0031fd60(void);
void func_00324d80(struct S *p){ func_00324c18(p); do { func_0031fd60(); } while (p->b49); }
