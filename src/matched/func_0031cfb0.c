/* func_0031cfb0 : pass aligned D address + 0x800 as 5th/6th args (EABI) */
extern char D_0081CF4F[];
extern void func_0031d258(int, int, int, int, void *, int);

void func_0031cfb0(int a, int b, int c, int d)
{
  func_0031d258(a, b, c, d, (void *)((unsigned int)(unsigned long)D_0081CF4F & ~0x3Fu), 0x800);
}
