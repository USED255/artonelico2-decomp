
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
M2C_UNK func_00120340(void *, M2C_UNK, s16);
M2C_UNK func_00144bc0(void *);
void func_00144dc0(void *arg0)
{
  int new_var2;
  s8 *new_var;
  s16 temp_s1;
  s16 temp_t6;
  s16 temp_s1_2;
  temp_t6 = *((s16 *) (((s8 *) (*((void **) (((s8 *) arg0) + 0xC)))) + 8));
  temp_s1 = *((s16 *) (((s8 *) arg0) + 0x85A));
  new_var2 = temp_s1 >= temp_t6;
  temp_s1_2 = (new_var2) ? (temp_t6) : (temp_s1);
  new_var = ((s8 *) arg0) + 0x420;
  func_00120340(arg0 + 0x14, 1, temp_s1);
  *((s16 *) (((s8 *) arg0) + 0x41C)) = temp_s1_2;
  *((s32 *) (((s8 *) arg0) + 0x420)) = (s32) ((*((s32 *) new_var)) | 0x600);
  func_00144bc0(arg0);
}
