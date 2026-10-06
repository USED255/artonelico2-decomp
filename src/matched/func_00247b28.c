
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
extern M2C_UNK D_00C082A8;
void func_00247b28(u32 arg0, s32 arg1)
{
  s32 temp_t7;
  u8 *temp_t5;
  if (arg0 < 0x15AU)
  {
    temp_t5 = &D_00C082A8;
    temp_t5 = arg0 + temp_t5;
    ;
    *temp_t5 = (u8) ((((*temp_t5) + arg1) >= 0x100) ? (0xFF) : ((*temp_t5) + arg1));
  }
}
