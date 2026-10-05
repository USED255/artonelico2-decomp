
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
extern int func_001ef0f0();
void func_001ef628(int param_1)
{
  int new_var;
  new_var = 0;
  if ((((*((ulong *) (param_1 + 0x98))) & 1) != new_var) && ((((*((ulong *) (param_1 + 0xa8))) & 0x8000000000000) != new_var) || ((*((short *) (param_1 + 0xb4))) == new_var)))
  {
    func_001ef0f0();
  }
  return;
}
