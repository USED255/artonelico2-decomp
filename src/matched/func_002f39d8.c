struct S { char pad[0x2038]; int f2038; };
extern int func_002ece80(struct S *, int, int *);
void func_002f39d8(struct S *p, int *out){ int buf[8]; if (func_002ece80(p, p->f2038, buf)) { out[0] = 0; out[1] = 0; } else { out[0] = buf[0]; out[1] = buf[1]; } }
