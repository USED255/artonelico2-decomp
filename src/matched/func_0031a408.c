struct S { char pad[8]; int fd; char pad2[0xA0]; };
extern void func_0032c080(int, void *, void *);
extern void func_0032c0b8(int, void *, void *, void *);
void func_0031a408(struct S *p){ func_0032c080(p->fd, (char *)p + 0xAC, (char *)p + 0xB0); func_0032c0b8(p->fd, (char *)p + 0xA6, (char *)p + 0xA8, (char *)p + 0xAA); }
