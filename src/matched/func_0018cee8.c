/* func_0018cee8 @ 0x0018cee8 (32 B) : initialise D_009DFCD8 {char,short,short,short} */
struct G {
  char f0;      /* 0x0 */
  short f2;     /* 0x2 */
  short f4;     /* 0x4 */
  short f6;     /* 0x6 */
};

extern struct G D_009DFCD8;

void func_0018cee8(int a, int b, int c)
{
  D_009DFCD8.f0 = 1;
  D_009DFCD8.f2 = (short)a;
  D_009DFCD8.f4 = (short)b;
  D_009DFCD8.f6 = (short)c;
}
