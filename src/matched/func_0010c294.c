
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
extern int func_0010c1ec();
void func_0010c294(int param_1)
{
  int new_var2;
  char *new_var4;
  unsigned long long new_var6;
  int new_var5;
  char *new_var3;
  char *new_var;
  new_var2 = param_1 + 0x40;
  new_var = (char *) new_var2;
  new_var4 = (new_var3 = &(*new_var));
  new_var6 = '\0';
  new_var5 = (*new_var4) == new_var6;
  if (new_var5)
  {
    func_0010c1ec();
    return;
  }
  return;
}
