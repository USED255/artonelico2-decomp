
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
extern int func_0010e4b4();
extern int func_0010e504();
extern int func_00168e3c();
void func_0016a064(undefined8 param_1, int param_2)
{
  char cVar1;
  int iVar2;
  unsigned int new_var;
  undefined4 *puVar3;
  char cVar4;
  puVar3 = *((undefined4 **) (param_2 + 0x10030));
  if ((*((char *) (param_2 + 0x10034))) == '\0')
  {
    cVar4 = -1;
    func_0010e504(param_1, 1);
    iVar2 = puVar3[1];
    while (1)
    {
      if (iVar2 == 0)
      {
        puVar3 = (undefined4 *) (*puVar3);
      }
      else
      {
        cVar1 = *((char *) (puVar3 + 3));
        if (cVar1 != cVar4)
        {
          new_var = (cVar4 = cVar1);
          func_0010e4b4(param_1, new_var, 0x80);
        }
        func_00168e3c(param_1, puVar3);
        puVar3 = (undefined4 *) (*puVar3);
      }
      if (puVar3 == ((undefined4 *) 0x0))
      {
        break;
      }
      iVar2 = puVar3[1];
    }

    func_0010e4b4(param_1, 1, 0x80);
    func_0010e504(param_1, 0);
    return;
  }
  return;
}
