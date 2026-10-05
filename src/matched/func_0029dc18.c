
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
extern int LibcString_13();
void func_0029dc18(int param_1)
{
  int new_var2;
  int new_var;
  int iVar1;
  int new_var3;
  int new_var4;
  new_var3 = param_1 + 0x540;
  new_var = (param_1 + ((*((int *) (param_1 + 0x53c))) * 0x40)) + 0x30;
  LibcString_13(new_var);
  iVar1 = (*((int *) (param_1 + 0x53c))) + 1;
  *((int *) (param_1 + 0x53c)) = iVar1;
  *((int *) (param_1 + 0x534)) = (*((int *) (param_1 + 0x534))) + (new_var2 = 1);
  new_var = param_1;
  if (0x13 < iVar1)
  {
    *((undefined4 *) (new_var + 0x53c)) = 0;
  }
  if ((*((int *) (new_var + 0x53c))) == (new_var4 = *((int *) new_var3)))
  {
    *((int *) (new_var + 0x540)) = (*((int *) (new_var + 0x53c))) + new_var2;
    *((int *) (new_var + 0x534)) = (*((int *) (new_var + 0x534))) + (-new_var2);
  }
  if ((*((int *) (new_var + 0x530))) == 0)
  {
    *((undefined4 *) (new_var + 0x530)) = new_var2;
  }
  if (new_var)
  {
    return;
  }
  else
  {
    return;
  }
}
