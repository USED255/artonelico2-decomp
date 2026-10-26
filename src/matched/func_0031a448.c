struct S { char pad[8]; int fd; char pad2[0xA0]; };
extern void func_0032c058(int, void *, void *);
extern void func_0032c0a8(int, short, short, short);
void func_0031a448(struct S *p){ func_0032c058(p->fd, (char *)p + 0xAC, (char *)p + 0xB0); func_0032c0a8(p->fd, *(short *)((char *)p + 0xA6), *(short *)((char *)p + 0xA8), *(short *)((char *)p + 0xAA)); }
