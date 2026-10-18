
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
typedef unsigned char uint8_t;
typedef signed char int8_t;
typedef unsigned short uint16_t;
typedef short int16_t;
typedef unsigned int uint32_t;
typedef int int32_t;
typedef unsigned long long uint64_t;
typedef long long int64_t;
typedef unsigned int uintptr_t;
typedef int intptr_t;
typedef unsigned int size_t;
typedef int ssize_t;
typedef int ptrdiff_t;
typedef int BOOL;
int baseelf_87();
int func_0011f118();
int func_001326f4();
int func_0013787c();
int func_0013fec0();
int func_00144d4c();
int func_00146880();
int func_001a15f4();
int func_00270ed8();
int func_00271134();
int func_00278ff4();
int func_00279418();
int func_0027bbd0();
int func_0027c4c4();
int func_0027c844();
int func_0027cd10();
void func_0028ad38(s32 arg0, void *arg1)
{
  void *s1 = arg1;
  s32 s0 = arg0;
  s32 s2;
  int new_var;
  s32 t7;
  t7 = *((s16 *) (((uintptr_t) arg1) + 0x2344));
  if (t7 >= 0)
  {
    goto Lskip_call;
  }
  func_001a15f4();
  Lskip_call:
  baseelf_87(arg0);

  t7 = *((s16 *) (((uintptr_t) s1) + 0x2344));
  if (t7 < 0)
  {
    goto L_else2;
  }
  func_0013787c((unsigned long long) arg0, (void *) (((uintptr_t) s1) + 0x40C));
  func_0011f118(arg0, (void *) (((uintptr_t) arg1) + 0x1A2C));
  func_0027c844(arg0, (void *) (((uintptr_t) arg1) + 0x1EAC));
  goto L_after_else2;
  L_else2:
  func_00271134(arg0, (void *) (((uintptr_t) s1) + 0x40C));

  L_after_else2:
  baseelf_87(arg0);

  s2 = 0x20000;
  {
    uint32_t *p = *((uint32_t **) (((uintptr_t) s1) + 0x2304));
    uint32_t v = *((uint32_t *) (((uint8_t *) p) + 0x10C));
    if ((v & s2) == 0)
    {
      func_00146880(arg0);
    }
  }
  func_00144d4c(arg0, (void *) (((uintptr_t) s1) + 0x848));
  func_00279418(arg0, (void *) (((uintptr_t) s1) + 0x424));
  func_00278ff4(arg0, *((void **) (((uintptr_t) s1) + 0x2304)));
  func_0027bbd0(arg0, (void *) (((uintptr_t) s1) + 0x10B4));
  func_0027c4c4(arg0, (void *) (((uintptr_t) s1) + 0x19B8));
  func_0011f118(arg0, (void *) (((uintptr_t) s1) + 0x19FC));
  new_var = 0x10C;
  {
    uint32_t *p = *((uint32_t **) (((uintptr_t) s1) + 0x2304));
    uint32_t v = *((uint32_t *) (((uint8_t *) p) + new_var));
    if ((v & s2) != 0)
    {
      func_00146880(arg0);
    }
  }
  func_00270ed8(arg0, (void *) (((uintptr_t) s1) + 0x19E8));
  func_0027cd10(arg0, (void *) (((uintptr_t) s1) + 0x1A5C));
  func_0013fec0(arg0);
  baseelf_87(arg0);
  return func_001326f4(arg0, (void *) (((uintptr_t) s1) + 0x1ED4));
}
