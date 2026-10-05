
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
volatile char func_001004e8(s16);
M2C_UNK func_00236374(M2C_UNK);
s16 func_0027b308(s16);
void func_0028bc6c(void *arg0)
{
  unsigned int temp_v0;
  temp_v0 = func_0027b308(*((s16 *) (((s8 *) arg0) + 0x233E)));
  *((s16 *) (((s8 *) arg0) + 0x2340)) = temp_v0;
  if (arg0)
  {
  }
  *((s32 *) (((s8 *) arg0) + 0x2308)) = func_001004e8(temp_v0);
  func_00236374(1);
}
