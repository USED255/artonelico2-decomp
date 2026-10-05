
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
M2C_UNK func_0014c0c8(s32);
void func_001effc4(void *arg0, s32 arg1, int arg2)
{
  if ((arg1 >= 0) && ((*((s16 *) (((s8 *) arg0) + 0xFC))) < arg2))
  {
    func_0014c0c8(arg1);
    *((s16 *) (((s8 *) arg0) + 0xFC)) = arg2;
  }
}
