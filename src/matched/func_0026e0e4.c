
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
extern int func_00147eac();
extern char D_00586E50;
extern unsigned int D_007FE564;
void func_0026e0e4(void)
{
  int iVar1;
  ulong uVar2;
  func_00147eac();
  iVar1 = D_007FE564;
  uVar2 = *((ulong *) (D_007FE564 + 0x558));
  *((ulong *) (iVar1 + 0x558)) = uVar2 & 0xfffffffffffffffe;
  *((undefined2 *) (iVar1 + 0x540)) = 0xe;
  *((undefined2 *) (iVar1 + 0x53c)) = 0xff83;
  *((undefined2 *) (iVar1 + 0x53e)) = 0xff83;
  *((undefined2 *) (iVar1 + 0x544)) = 0xffff;
  *((undefined2 *) (D_007FE564 + 0x546)) = 0xffff;
  D_00586E50 = 0;
  return;
}
