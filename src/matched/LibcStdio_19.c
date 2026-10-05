
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
M2C_UNK func_0035f5c0(void *);
M2C_UNK func_00367050(void *, void *, M2C_UNK, M2C_UNK);
extern void *D_0083E7F8;
void LibcStdio_19(void *arg0, M2C_UNK arg1, M2C_UNK arg2)
{
  void *new_var2;
  void *var_a0;
  int new_var;
  var_a0 = *((void **) (((s8 *) arg0) + 0x54));
  if (var_a0 == 0)
  {
    new_var2 = D_0083E7F8;
    *((void **) (((s8 *) arg0) + 0x54)) = (void *) new_var2;
    var_a0 = new_var2;
  }
  if ((*((s32 *) (((s8 *) var_a0) + 0x38))) == 0)
  {
    func_0035f5c0(var_a0);
  }
  func_00367050(*((void **) (((s8 *) arg0) + (new_var = 0x54))), arg0, arg1, arg2);
}
