
typedef unsigned char undefined;
typedef unsigned char undefined1;
typedef unsigned short short;
typedef unsigned int undefined4;
typedef unsigned long long undefined8;
typedef unsigned int uint;
typedef unsigned long ulong;
typedef unsigned short ushort;
typedef unsigned char uchar;
typedef long long longlong;
typedef unsigned long long ulonglong;
typedef unsigned char byte;
typedef unsigned char code;
typedef unsigned char bool;
typedef struct 
{
  int a[3];
} int3;
typedef struct 
{
  unsigned int a[3];
} uint3;
extern unsigned int _CONCAT44(unsigned int, unsigned int);
extern unsigned long long _CONCAT82(unsigned int, unsigned int);
extern void SYNC(int);
extern void EI(void);
extern void DI(void);
extern void FlushCache(int);
extern int syscall(int);
extern int baseelf_18();
extern int func_00233334();
extern int func_002338bc();
extern int func_00270e64();
extern int func_0027a33c();
void func_0023051c(int param_1)
{
  int new_var;
  int iVar1;
  func_0027a33c(param_1 + 0x32c0, 2);
  *((undefined1 *) (param_1 + 0x32c1)) = *((undefined1 *) (param_1 + 0x32c3));
  *((undefined1 *) (param_1 + 0x32c2)) = 0x10;
  *((short *) (param_1 + 0x3584)) = 0xffff;
  func_00270e64(param_1 + 0x34f0, 0);
  *((short *) (param_1 + 0x3586)) = 2;
  *((short *) (param_1 + 0x3588)) = 0;
  *((ulong *) (param_1 + 0x3588)) = (*((ulong *) (param_1 + 0x3588))) & 0xfffffffffffeffff;
  func_00233334(param_1 + 0x28dc);
  iVar1 = baseelf_18(0);
  func_002338bc(param_1 + 0x28dc, *((short *) (iVar1 + 0x1e)), *((short *) (param_1 + 0x3586)), *((short *) (param_1 + 0x3588)), (short) ((new_var = ((int) (*((undefined8 *) (param_1 + 0x3588)))) << 0xf) >> 0x1f));
  *((undefined1 *) (param_1 + 0x28dd)) = *((undefined1 *) (param_1 + 0x28df));
  *((undefined1 *) (param_1 + 0x28de)) = 0x10;
  return;
}
