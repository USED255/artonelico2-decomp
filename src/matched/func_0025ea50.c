
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
extern int baseelf_87();
extern int func_0011f118();
extern int func_001326f4();
extern int func_001942e0();
extern int func_00194430();
extern int func_0019470c();
extern int func_0027c844();
void func_0025ea50(undefined8 param_1, int param_2, int param_3)
{
  func_001942e0();
  func_0027c844(param_1, param_3 + 0x127c);
  func_0011f118(param_1, param_3 + 0x12ec);
  func_00194430(param_1, param_2);
  func_0011f118(param_1, param_3 + 0x12bc);
  func_0019470c(param_1, param_2);
  baseelf_87(param_1);
  func_001326f4(param_1, ((int) param_2) + 0x834);
  return;
}
