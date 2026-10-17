
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
M2C_UNK func_00183b64(s32);
void baseelf_181(void *arg0)
{
  s32 temp_a0;
  s32 var_s0;
  int new_var;
  s32 var_t5;
  void *var_t6;
  var_s0 = 0;
  do
  {
    temp_a0 = arg0 + (var_s0 * 0x50);
    var_s0 += 1;
    func_00183b64(temp_a0);
  }
  while (var_s0 < 0x32);
  *((s32 *) (((s8 *) arg0) + 0xFA0)) = 0;
  *((s16 *) (((s8 *) arg0) + 0xFAE)) = -1;
  *((s32 *) (((s8 *) arg0) + 0xFA4)) = 0;
  var_t5 = 0xE;
  *((s32 *) (((s8 *) arg0) + 0xFA8)) = 0;
  var_t6 = arg0;
  *((s16 *) (((s8 *) arg0) + 0xFAC)) = -1;
  *((s32 *) (((s8 *) arg0) + 0xFD0)) = 0;
  do
  {
    new_var = -1;
    var_t5 -= 1;
    *((s8 *) (((s8 *) var_t6) + 0xFBF)) = new_var;
    *((s8 *) (((s8 *) var_t6) + 0xFB0)) = -1;
    var_t6 += 1;
  }
  while (var_t5 >= 0);
}
