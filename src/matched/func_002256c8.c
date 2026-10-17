typedef int s32;
typedef unsigned int u32;
typedef unsigned char u8;

s32 func_002256c8(u8 *a0) {
    switch (*(u32 *)(a0 + 0x50)) {
    case 0: return 0x96;
    case 1: return 0x7D;
    case 2: return 0x64;
    case 3: return 0x5A;
    case 4:
    case 5:
    default: return 0x4B;
    }
}
