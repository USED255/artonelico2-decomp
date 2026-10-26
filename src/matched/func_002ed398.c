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
s32 func_002ed398(char *a0, s32 a1)
{
  s32 t = a1 << 3;
  t -= a1;
  t <<= 2;
  t += a1;
  t <<= 2;
  return *(s32 *) (a0 + t + 5044);
}
