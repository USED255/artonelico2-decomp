
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
extern int func_0014c0c8();
void func_00224cdc(int param_1)
{
  undefined8 uVar1;
  undefined4 new_var;
  new_var = *((undefined4 *) ((*((int *) (param_1 + 0x40c))) + 0x50));
  if ((*((char *) (param_1 + 0x6f83))) == '\0')
  {
    switch (new_var)
    {
      case 0:
        uVar1 = 0xf2;
        break;

      case 1:
        uVar1 = 0xfd;
        break;

      case 2:
        uVar1 = 0xe4;
        break;

      case 3:
        uVar1 = 0x11f;
        break;

      case 4:
        uVar1 = 0x11c;
        break;

      default:
        goto switchD_00224d10_default;

    }

    func_0014c0c8(uVar1);
  }
  switchD_00224d10_default:
  return;

}
