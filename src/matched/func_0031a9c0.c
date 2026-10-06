/* Ar tonelico II (SLPS_258.19) matching decompilation — CRI ADX middleware.
 *
 * Function body recovered from recvx-decomp (MIT licence), which decompiled the
 * same CRI ADX EE library for Resident Evil: Code Veronica X:
 *   https://github.com/AshfordFamily/recvx-decomp  src/cri/mwlib/ee/lib/libadxe/adx_bsc.c
 * Adapted to this build (symbol name = retail address, self-contained decls).
 * Original CRI ADX version here: ADXT 10.03 / ADXRT 3100 (Build:Feb  9 2007).
 */
typedef signed char        s8;
typedef unsigned char      u8;
typedef signed short       s16;
typedef unsigned short     u16;
typedef signed int         s32;
typedef unsigned int       u32;
typedef float              f32;
#define NULL ((void*)0)
typedef double             f64;

typedef s32 Sint32;  typedef u32 Uint32;
typedef s16 Sint16;  typedef u16 Uint16;
typedef s8  Sint8;   typedef u8  Uint8;
typedef f32 Float32;












//#include <string.h>


void func_0031a9c0(Sint16 *dst, const Sint16 *src, Sint32 nword)
{
    for ( ; nword > 0; nword--) 
    {
        *dst++ = *src++;
    }
}
