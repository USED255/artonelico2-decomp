
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
s32 func_001e4030(M2C_UNK);
s32 func_001e41b8(M2C_UNK);
s32 func_001e6f24(M2C_UNK);
M2C_UNK func_001f74d4();
extern void *D_007AF2D0;
s32 func_001f7364(void)
{
  s32 *var_t6;
  s32 temp_v0;
  s32 var_t7;
  if ((func_001e6f24(0) == 0) && (func_001e6f24(1) == 0))
  {
    var_t6 = *((s32 **) (((s8 *) D_007AF2D0) + 0xC1C30));
    var_t7 = 2;
    goto block_7;
  }
  if (func_001e6f24(0) == 0)
  {
    var_t6 = *((s32 **) (((s8 *) D_007AF2D0) + 0xC1C30));
    var_t7 = 1;
    goto block_7;
  }
  if (func_001e6f24(1) == 0)
  {
    var_t6 = *((s32 **) (((s8 *) D_007AF2D0) + 0xC1C30));
    var_t7 = 4;
    block_7:
    *var_t6 = var_t7;

  }
  if (func_001e41b8(0x10) != 0)
  {
    *(*((s32 **) (((s8 *) D_007AF2D0) + 0xC1C30))) = 3;
  }
  temp_v0 = func_001e4030(0x11);
  if ((temp_v0 > 0) && (func_001e4030(0) >= temp_v0))
  {
    *(*((s32 **) (((s8 *) D_007AF2D0) + 0xC1C30))) = 4;
  }
  if (func_001e41b8(0x14) != 0)
  {
    *(*((s32 **) (((s8 *) D_007AF2D0) + 0xC1C30))) = 4;
  }
  var_t7 = (*(*((s32 **) (((s8 *) D_007AF2D0) + 0xC1C30)))) != 0;
  if (var_t7)
  {
    func_001f74d4();
  }
  return *(*((s32 **) (((s8 *) D_007AF2D0) + 0xC1C30)));
}
