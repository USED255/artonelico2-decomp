
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
extern int func_00140b98();
extern int func_00145960();
extern unsigned int D_007EADA0;
void func_0024718c(void)
{
  unsigned int new_var;
  undefined4 *new_var2;
  unsigned int new_var3;
  if (new_var2)
  {
    func_00145960();
    new_var = D_007EADA0;
    new_var3 = new_var;
    new_var2 = (undefined4 *) (new_var3 + 4);
    func_00140b98(*new_var2, 1);
    return;
  }
  else
  {
    func_00145960();
    new_var = D_007EADA0;
    new_var3 = new_var;
    new_var2 = (undefined4 *) (new_var3 + 4);
    func_00140b98(*new_var2, 1);
    return;
  }
}
