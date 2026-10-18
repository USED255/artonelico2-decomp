
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
extern char D_00BB71D0;
extern unsigned int _CONCAT44(unsigned int, unsigned int);
extern unsigned long long _CONCAT82(unsigned int, unsigned int);
extern void SYNC(int);
extern void EI(void);
extern void DI(void);
extern void FlushCache(int);
extern int syscall(int);
extern int func_0010e4d4();
extern int func_0011299c();
extern int baseelf_153();
extern int func_0013e2fc();
extern int func_002735e4();
void func_00258898(undefined8 param_1, int param_2)
{
  int iVar1;
  unsigned char *pcVar2;
  int iVar3;
  int iVar4;
  pcVar2 = (unsigned char *) param_2;
  if (((-1) < (*((short *) (pcVar2 + 0x42)))) && ((*((int *) (pcVar2 + 8))) != 0))
  {
    func_0013e2fc(param_2);
    if ((*pcVar2) != '\0')
    {
      func_0011299c(*pcVar2);
      baseelf_153(param_1, *((undefined4 *) (pcVar2 + 8)), *((short *) (pcVar2 + 0x48)), *((short *) (pcVar2 + 0x4a)));
      if ((*((short *) (pcVar2 + 0x44))) == 0)
      {
        iVar1 = *((int *) (pcVar2 + 8));
        iVar4 = ((int) (*((short *) (pcVar2 + 0x48)))) + ((int) (*((short *) (iVar1 + 100))));
        iVar3 = ((int) (*((short *) (pcVar2 + 0x4a)))) + ((int) (*((short *) (iVar1 + 0x66))));
        func_0010e4d4(param_1, iVar4 + 3, iVar3 + 5, (iVar4 + (*((int *) (iVar1 + 0x70)))) + (-4), (iVar3 + (*((int *) (iVar1 + 0x74)))) + (-4));
        func_002735e4((&D_00BB71D0), pcVar2 + 0xc);
        func_0010e4d4(param_1, 0, 0, 0x27f, 0x1bf);
      }
      func_0011299c(0x80);
      return;
    }
  }
  return;
}
