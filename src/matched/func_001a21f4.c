/* func_001a21f4 @ 0x001a21f4 (28 B) : write two bytes at D_00BFCC10+0x3D/0x3E and a word at D_00BC4120 */
struct A {
  char pad_0x0[0x3D];
  char x;       /* 0x3D */
  char y;       /* 0x3E */
};

extern struct A D_00BFCC10;
extern int D_00BC4120;

void func_001a21f4(int a, int b, int c)
{
  D_00BFCC10.x = (char)a;
  D_00BFCC10.y = (char)b;
  D_00BC4120 = c;
}
