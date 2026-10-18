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
void func_001a9938(char *a0, f32 a1)
{
  *(s32 *) (a0 + 300) = 0;
  *(f32 *) (a0 + 288) = a1;
  *(f32 *) (a0 + 292) = a1;
  *(f32 *) (a0 + 296) = a1;
}
