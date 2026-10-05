
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
extern int func_001e41f8();
void func_001858ac(int param_1)
{
  short new_var3;
  int new_var;
  undefined2 *new_var2;
  new_var = '\0';
  if ((*((char *) (param_1 - -0x1a))) == '\0')
  {
    ;
    new_var2 = (undefined2 *) (param_1 + 0x14);
    new_var3 = *new_var2;
    func_001e41f8(new_var3);
 do { } while (0);
    return;
  }
  return;
}
