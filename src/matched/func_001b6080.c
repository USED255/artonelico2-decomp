
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
M2C_UNK func_001b6040(void *);
void func_001b6080(void *arg0)
{
  s32 var_s2;
  void *var_s0;
  var_s0 = arg0;
  var_s2 = 0x27;
  do
  {
    var_s2 -= 1;
    func_001b6040(var_s0);
    var_s0 += 0x40;
  }
  while (var_s2 >= 0);
  *((s32 *) (((s8 *) arg0) + 0xA00)) = 0;
  *((s32 *) (((s8 *) arg0) + 0xA08)) = (*((s32 *) (((s8 *) arg0) + 0xA04)) = 0);
  *((s16 *) (((s8 *) arg0) + 0xA0C)) = -1;
  *((s16 *) (((s8 *) arg0) + 0xA0E)) = -1;
}
