
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
extern int func_0029c004();
extern int func_0029c134();
extern char D_00BB9298;
extern unsigned int D_00C0D11C;
undefined8 func_0029ce50(int param_1)
{
  int iVar1;
  int iVar2;
  char *pcVar3;
  iVar2 = 0;
  pcVar3 = &D_00C0D11C;
  do
  {
    iVar1 = func_0029c004(iVar2);
    if ((((((*pcVar3) == '\x02') && ((*((short *) (iVar1 + 0x1a))) != (-1))) && ((*((short *) (iVar1 + 0x1a))) != 0)) && ((*((int *) (pcVar3 + 4))) != (-1))) && (((*((int *) (pcVar3 + 4))) <= param_1) || (((*((short *) (iVar1 + 0x1e))) != (-1)) && ((&D_00BB9298)[(*((short *) (iVar1 + 0x1e))) * 4] != '\0'))))
    {
      func_0029c134(iVar2, 5);
    }
    iVar2 = iVar2 + 1;
    pcVar3 = pcVar3 + 8;
  }
  while (iVar2 < 0x3c);
  return 0;
}
