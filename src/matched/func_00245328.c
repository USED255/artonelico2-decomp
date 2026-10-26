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
extern s8 D_00C07888[];
void func_00245328(s32 a0, u32 a1)
{
  D_00C07888[a0 * 8 + 1] = a1;
}
