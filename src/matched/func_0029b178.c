
typedef signed char s8;
typedef unsigned char u8;
typedef short s16;
typedef unsigned short u16;
typedef int s32;
typedef unsigned int u32;
typedef long long s64;
typedef unsigned long long u64;
typedef float f32;
typedef double f64;
typedef unsigned char undefined1;
typedef unsigned short undefined2;
typedef unsigned int undefined4;
typedef unsigned long long undefined8;
typedef unsigned char byte;
typedef unsigned char code;
typedef unsigned int uint;
typedef int s128;
typedef int u128;
typedef int s64_;
extern unsigned char *sp;
typedef s32 M2C_UNK;
typedef s8 M2C_UNK8;
typedef s16 M2C_UNK16;
typedef s32 M2C_UNK32;
typedef s64 M2C_UNK64;
M2C_UNK func_0011a200(M2C_UNK *);
M2C_UNK func_0013e2e8();
unsigned long func_0029b4f4(void *);
extern M2C_UNK D_003C4718;
extern M2C_UNK D_0054AA00;
void func_0029b178(void *arg0)
{
  int new_var;
  int new_var3;
  M2C_UNK *new_var2;
  if (new_var)
  {
    new_var2 = &D_0054AA00;
    *((u16 *) (((s8 *) arg0) + 6)) = (u16) (*((u16 *) (((s8 *) new_var2) + 0x47C)));
    new_var = 0x47E;
    *((u16 *) (((s8 *) arg0) + 8)) = (u16) (*((u16 *) (((s8 *) (&D_0054AA00)) + new_var)));
    func_0013e2e8();
    *((s8 *) (((s8 *) arg0) + 4)) = 0;
    *((s8 *) (((s8 *) arg0) + 3)) = -0x80;
    new_var3 = 0;
    *((s8 *) (((s8 *) arg0) + 0)) = new_var3;
    *((s8 *) (((s8 *) arg0) + 2)) = 0;
    func_0011a200(&D_003C4718);
    func_0029b4f4(arg0);
  }
  else
  {
    new_var2 = &D_0054AA00;
    *((u16 *) (((s8 *) arg0) + 6)) = (u16) (*((u16 *) (((s8 *) new_var2) + 0x47C)));
    new_var = 0x47E;
    *((u16 *) (((s8 *) arg0) + 8)) = (u16) (*((u16 *) (((s8 *) (&D_0054AA00)) + new_var)));
    func_0013e2e8();
    *((s8 *) (((s8 *) arg0) + 4)) = 0;
    *((s8 *) (((s8 *) arg0) + 3)) = -0x80;
    new_var3 = 0;
    *((s8 *) (((s8 *) arg0) + 0)) = new_var3;
    *((s8 *) (((s8 *) arg0) + 2)) = 0;
    func_0011a200(&D_003C4718);
    func_0029b4f4(arg0);
  }
}
