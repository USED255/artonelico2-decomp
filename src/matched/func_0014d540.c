
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
M2C_UNK func_0014d218(s16);
extern volatile unsigned char D_00AF29A8;
void func_0014d540(s32 arg0)
{
  s16 temp_t6;
  void *temp_a0;
  temp_a0 = ((arg0 * 2) * 2) + (&D_00AF29A8);
  temp_t6 = *((s16 *) (((s8 *) temp_a0) + 0));
  *((s16 *) (((s8 *) temp_a0) + 0)) = (*((s16 *) (((s8 *) temp_a0) + 2)) = -1);
  func_0014d218(temp_t6);
}
