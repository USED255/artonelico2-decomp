/* func_00239654 @ 0x00239654 (24 B) : store three words at D_00BFF400[0..2] */
struct G {
  int a;        /* 0x0 */
  int b;        /* 0x4 */
  int c;        /* 0x8 */
};

extern struct G D_00BFF400;

void func_00239654(int a, int b, int c)
{
  D_00BFF400.a = a;
  D_00BFF400.b = b;
  D_00BFF400.c = c;
}
