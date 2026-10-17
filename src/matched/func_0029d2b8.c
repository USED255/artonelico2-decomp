
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
M2C_UNK func_0011a200(M2C_UNK *);
M2C_UNK func_0013e2e8();
short func_00271d8c(void *);
M2C_UNK func_00271e04(void *, s32, s32);
extern M2C_UNK D_003BE208;
void func_0029d2b8(void *arg0)
{
  void *temp_s2;
  M2C_UNK *new_var;
  func_0013e2e8();
  *((s8 *) (((s8 *) arg0) + 0)) = 0;
  *((s8 *) (((s8 *) arg0) + 3)) = -0x80;
  temp_s2 = arg0 + 6;
 goto dummy_label_157634; dummy_label_157634: ;
  *((s8 *) (((s8 *) arg0) + 4)) = (*((s8 *) (((s8 *) arg0) + 2)) = 0);
  new_var = &D_003BE208;
  *((s16 *) (((s8 *) new_var) + 0x98)) = -1;
 do { func_00271d8c(temp_s2); } while (0); new_var = new_var;
  func_00271e04(temp_s2, ((*((s16 *) (((s8 *) new_var) + 0x64))) + (((s32) ((*((u32 *) (((s8 *) new_var) + 0x70))) + (((u32) (*((u32 *) (((s8 *) new_var) + 0x70)))) >> 0x1F))) >> 1)) + 0x154, ((*((s16 *) (((s8 *) new_var) + 0x66))) + (((s32) ((*((u32 *) (((s8 *) new_var) + 0x74))) + (((u32) (*((u32 *) (((s8 *) new_var) + 0x74)))) >> 0x1F))) >> 1)) + 0xDC);
  func_0011a200(new_var);
}
