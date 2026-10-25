/* func_002ffc08 @ 0x002ffc08 (28 B, CRI) : initialise {s64,s64,s64,int} struct */
struct S {
  long long a;      /* 0x0 */
  long long b;      /* 0x8 */
  long long c;      /* 0x10 */
  int d;            /* 0x18 */
};

void func_002ffc08(struct S *p)
{
  p->a = 0;
  p->b = 0x7FFFFFFFFFFFFFFFLL;
  p->c = 0;
  p->d = 0;
}
