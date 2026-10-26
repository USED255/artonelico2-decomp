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
extern unsigned char *sp;
typedef s32 M2C_UNK;
s32 func_002b3858(char *a0, s32 a1)
{
  s32 v = *(s32 *) (a0 + 12);
  s32 t = (v << 5) + 16;
  return (a0 + a1 * 16) + t;
}
