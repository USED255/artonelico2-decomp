
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
extern int func_00132448();
extern int func_00181c0c();
extern int func_00184c84();
extern int baseelf_35();
extern int func_001e41b8();
extern int func_001e4538();
extern int func_001e45f0();
extern int func_001e701c();
extern int func_001e72c0();
extern int func_001e7a5c();
extern int baseelf_139();
extern int func_001edc94();
extern int func_001ee66c();
extern int func_001f1660();
extern int func_001f53f4();
extern int func_001fa310();
extern int func_0022001c();
extern int func_002261cc();
extern int func_00228f74();
extern unsigned int D_009DFCD4;
extern unsigned int D_00A50550;
void func_001e1c00(int param_1)
{
  int lVar1;
  lVar1 = func_001e41b8(1);
  if (lVar1 != 0)
  {
    if ((D_00A50550 & 8) != 0)
    {
      func_001f53f4(2);
    }
    func_001e7a5c();
    func_001fa310(param_1 + 0xbe3b0);
    func_00181c0c();
    func_00184c84(D_009DFCD4 + 0x19d80);
    func_00184c84(D_009DFCD4 + 0x1ad60);
    func_001e45f0();
    func_001e4538();
    lVar1 = func_001e41b8(10);
    if (lVar1 != 0)
    {
      func_001e701c();
    }
    lVar1 = func_001e72c0();
    if (lVar1 == 0)
    {
      baseelf_35(10, 0);
    }
    baseelf_139(param_1 + 0x63de0);
    func_00228f74(param_1 + 0xbf110);
    func_002261cc(param_1 + 0xc0920);
    func_001f1660(param_1 + 0x9e0);
    func_0022001c(param_1 + 0xbbb40);
    func_001ee66c(param_1 + 0x980, param_1 + 0x10);
    func_001edc94(param_1 + 0x10);
    func_00132448(param_1 + 0x212b0);
  }
  return;
}
