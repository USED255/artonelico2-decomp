typedef signed char s8; typedef unsigned char u8; typedef short s16; typedef int s32; typedef unsigned int u32;
extern unsigned char D_0054AA00[];
extern void baseelf_153(int, int, int, int);
void func_0025616c(int a0) {
    u32 off = 0x8000;
    u8 *p = (u8 *)D_0054AA00 + off;
    baseelf_153(a0, *(s32 *)(p + 0x25FC), *(s16 *)(p + 0x2604), *(s16 *)(p + 0x2606));
}
