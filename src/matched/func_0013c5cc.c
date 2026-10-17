
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
typedef unsigned char uint8_t;
typedef signed char int8_t;
typedef unsigned short uint16_t;
typedef short int16_t;
typedef unsigned int uint32_t;
typedef int int32_t;
typedef unsigned long long uint64_t;
typedef long long int64_t;
typedef unsigned int uintptr_t;
typedef int intptr_t;
typedef unsigned int size_t;
typedef int ssize_t;
typedef int ptrdiff_t;
typedef int BOOL;
int func_0013cbe4();
extern unsigned char D_00585540[];
extern unsigned char D_00585544[];
extern unsigned char D_00585548[];
s32 func_0013c5cc(s32 arg0, s32 arg1, s32 arg2, s32 *arg3, s32 arg4)
{
  s32 var_v0;
  if (arg0 != 0)
  {
    var_v0 = 1;
    *arg3 = 3;
  }
  else
  {
    func_0013cbe4(arg1, arg2, arg3, arg4);
    switch (*((u16 *) (&D_00585544)))
    {
      default:
        if ((*((s32 *) (&D_00585540))) > 0)
      {
        *((s32 *) (&D_00585540)) = -1;
      }
        break;

      case 0x0:
        *((s32 *) (&D_00585540)) = 0;
        break;

      case 0x9003:
        *((s32 *) (&D_00585540)) = -1;
        break;

      case 0x2F:
        if (((u32) (*((s32 *) (&D_00585540)))) < 2)
      {
        *((s32 *) (&D_00585540)) = -2;
      }
        break;

      case 0x13:
        *((s32 *) (&D_00585540)) = 1;
        break;

    }

    var_v0 = (*((s32 *) (&D_00585548))) != 1;
  }
  return var_v0;
}
