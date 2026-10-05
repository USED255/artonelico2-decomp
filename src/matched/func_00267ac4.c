
typedef unsigned char undefined;
typedef unsigned char undefined1;
typedef unsigned short undefined2;
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
extern int baseelf_145();
extern int func_00267990();
extern int func_00268384();
void func_00267ac4(int param_1, int param_2)
{
  char *pcVar1;
  int new_var;
  pcVar1 = (char *) param_1;
  if ((-1) < (*pcVar1))
  {
    baseelf_145(pcVar1 + 0x10);
    new_var = 0x100;
    func_00268384(param_2 + 0xb20, *pcVar1, pcVar1[1], pcVar1[2], pcVar1 + 0x20);
    if (((*((ulong *) (pcVar1 + 0x10))) & new_var) == 0)
    {
      func_00267990(param_1);
      return;
    }
  }
  return;
}
