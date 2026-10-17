
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
M2C_UNK func_00145330(void *, M2C_UNK);
M2C_UNK func_00238800(void *);
M2C_UNK func_0024b3c4(void *);
M2C_UNK func_0024fb74(void *);
M2C_UNK func_00276ad4(s32, M2C_UNK);
M2C_UNK func_00277dac(void *);
void func_00285280(void *arg0, s32 arg1)
{
  int new_var;
  u8 new_var2;
  if (arg1 != 0)
  {
    *((s8 *) (((s8 *) arg0) + 0x42A)) = 0;
    *((u8 *) (((s8 *) arg0) + 0x428)) = (u8) (*((u8 *) (((s8 *) arg0) + 0x42C)));
  }
  *((u8 *) (((s8 *) arg0) + 0x434)) = (u8) (*((u8 *) (((s8 *) arg0) + 0x438)));
  *((u8 *) (((s8 *) arg0) + 0x864)) = (u8) (*((u8 *) (((s8 *) arg0) + 0x868)));
  *((u8 *) (((s8 *) arg0) + 0xF1C)) = (u8) (*((u8 *) (((s8 *) arg0) + 0xF20)));
  *((u8 *) (((s8 *) arg0) + 0xF2A)) = (u8) (*((u8 *) (((s8 *) arg0) + 0xF2E)));
  *((s8 *) (((s8 *) arg0) + 0x436)) = 0;
  new_var = 0;
  *((s8 *) (((s8 *) arg0) + 0x866)) = 0;
  *((s8 *) (((s8 *) arg0) + 0xF1E)) = 0;
  *((s8 *) (((s8 *) arg0) + 0xF2C)) = 0;
  func_00276ad4(arg0 + 0xF34, 0);
  new_var2 = *((u8 *) (((s8 *) arg0) + 0xF38));
  *((u8 *) (((s8 *) arg0) + 0x1378)) = (u8) (*((u8 *) (((s8 *) arg0) + 0x137C)));
  *((u8 *) (((s8 *) arg0) + 0xF34)) = (u8) new_var2;
  *((s8 *) (((s8 *) arg0) + 0xF36)) = 0;
  *((s8 *) (((s8 *) arg0) + 0x137A)) = 0;
  func_00145330(arg0 + 0x138C, 0);
  func_00277dac(arg0 + 0x1384);
  func_0024b3c4(arg0 + 0x1C60);
  *((s8 *) (((s8 *) arg0) + 0x23D2)) = new_var;
  *((u8 *) (((s8 *) arg0) + 0x23D0)) = (u8) (*((u8 *) (((s8 *) arg0) + 0x23D4)));
  func_00238800(arg0 + 0x23EC);
  func_0024fb74(arg0 + 0x2420);
}
