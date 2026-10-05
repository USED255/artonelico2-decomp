
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
M2C_UNK func_0011f2bc(void *);
M2C_UNK func_0013e2e8();
M2C_UNK func_002793f4(void *, s16, s16);
extern volatile int D_0054AA00;
void func_0027939c(void *arg0)
{
  volatile int *new_var;
  func_0013e2e8();
  *((s8 *) (((s8 *) arg0) + 4)) = 0;
  *((s8 *) (((s8 *) arg0) + 3)) = -0x80;
  *((s8 *) (((s8 *) arg0) + 0)) = 0;
  *((s8 *) (((s8 *) arg0) + 2)) = 0;
  new_var = &D_0054AA00;
  func_002793f4(arg0, *((s16 *) (((s8 *) new_var) + 0x170)), *((s16 *) (((s8 *) new_var) + 0x172)));
  *((s16 *) (((s8 *) arg0) + 0x420)) = 0;
  func_0011f2bc(arg0 + 0xA);
}
