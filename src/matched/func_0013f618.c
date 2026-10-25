/* func_0013f618 @ 0x0013f618 (28 B) : write four bytes at D_00AF1490[0..3] */
struct S {
  char a;
  char b;
  char c;
  char d;
};

extern struct S D_00AF1490;

void func_0013f618(int a, int b, int c, int d)
{
  D_00AF1490.a = (char)a;
  D_00AF1490.b = (char)b;
  D_00AF1490.c = (char)c;
  D_00AF1490.d = (char)d;
}
