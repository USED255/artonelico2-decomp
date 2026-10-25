/* func_001d79ec @ 0x001d79ec (20 B) : initialise a {short,short,short,int} struct */
struct S {
  short a;      /* 0x0 */
  short b;      /* 0x2 */
  short c;      /* 0x4 */
  char pad[2];
  int d;        /* 0x8 */
};

void func_001d79ec(struct S *p)
{
  p->a = -1;
  p->b = 0;
  p->c = 0;
  p->d = 0;
}
