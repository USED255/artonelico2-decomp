/* Ar tonelico II (SLPS_258.19) matching decompilation — CRI ADX middleware.
 *
 * Function body recovered from recvx-decomp (MIT licence), which decompiled the
 * same CRI ADX EE library for Resident Evil: Code Veronica X:
 *   https://github.com/AshfordFamily/recvx-decomp  src/cri/mwlib/ee/lib/libadxe/adx_baif.c
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

#define SYNTH_S16(v) ((((v) & 0xFF00) >> 8) | (((v) << 8) & 0xFF00))
#define SYNTH_U16(v) ((Uint16)((((v) & 0xFF00) >> 8) | (((v) << 8) & 0xFF00)))
#define SYNTH_U32(v) ((((v) >> 24) & 0xFF) | (((v) >> 8) & 0xFF00) | (((v) << 8) & 0xFF0000) | ((v) << 24))
#define SYNTH_S32(v) ((Sint32)((((Uint32)(v)) >> 24) | ((v) << 24) | ((((v) << 8) & 0xFF0000) | (((v) >> 8) & 0xFF00))))
#define RD_I32(buf, i) ((buf)[(i)*4] | ((buf)[(i)*4+1] << 8) | ((buf)[(i)*4+2] << 16) | ((buf)[(i)*4+3] << 24))
#define RD_I16(buf, i) ((buf)[(i)*2] | ((buf)[(i)*2+1] << 8))

#define AIFF_IMAGIC 0x46464941
#define COMM_IMAGIC 0x4d4d4f43
#define SSND_IMAGIC 0x444e5353
#define FORM_IMAGIC 0x4D524F46
#define SND_IMAGIC 0x646E732E




//#include <string.h>

// 100% matching!

 void* func_00340548(void *hdr, Sint32 *sfreq, Sint32 *nch, Sint32 *bps, Sint32 *nsmpl)
{
	Uint8 *pdw;
	Uint8 *pdwEnd;
	Sint32 ck_id;
	Sint32 ck_size;
	Sint32 form_type;
	Sint32 comm_ck_flag;
	Sint32 ssnd_ck_flag;
	Uint32 ssnd_ofst;
	void *data;
    Uint32 tmp; 
    Sint32 temp, temp2, temp3, temp4;
    
    ssnd_ck_flag = comm_ck_flag = 0;
     
    data = NULL;

    pdw = hdr;

    ck_id = RD_I32(pdw, 0);
    
    pdw += 4;
    
    ck_size = RD_I32(pdw, 0);
    ck_size = SYNTH_U32(ck_size);
    
    pdw += 4;
    
    form_type = RD_I32(pdw, 0);
    
    pdw += 4;
    
    if (ck_id != FORM_IMAGIC) 
    {
        return NULL;
    }
    
    if (form_type != AIFF_IMAGIC) 
    {
        return NULL;
    }
    
    pdwEnd = (pdw + ck_size) - 4;

    while (pdw < pdwEnd) 
    {
        ck_id = RD_I32(pdw, 0);
        
        pdw += 4;
        
        ck_size = RD_I32(pdw, 0);
        ck_size = SYNTH_U32(ck_size);
        
        pdw += 4;
        
        switch (ck_id)
        {
        case COMM_IMAGIC:
            if (comm_ck_flag == 0) 
            {
                if (ck_size < 18) 
                {
                    return NULL;
                }
                
                ssnd_ofst = RD_I16(pdw, 0);
                
                *nch = SYNTH_U16(ssnd_ofst);
                
                pdw += 2;
                
                temp = RD_I32(pdw, 0);
                
                *nsmpl = SYNTH_S32(temp);
                
                pdw += 4;
                
                temp2 = RD_I16(pdw, 0);
                
                *bps = SYNTH_S16(temp2);
                
                pdw += 2;
                
                temp3 = RD_I16(pdw, 0);
                temp3 = SYNTH_U16(temp3);
                
                pdw += 2;
                
                temp4 = RD_I16(pdw, 0);
                
                *sfreq = SYNTH_U16(temp4);
                *sfreq = *sfreq >> (0x400E - temp3);
                
                pdw += 8;
                
                comm_ck_flag = 1;
                
                if (ssnd_ck_flag != 0) 
                {
                    return data;
                }
            }
            
            break;
        case SSND_IMAGIC:
            if (ssnd_ck_flag == 0)
            {
                tmp = RD_I32(pdw, 0);
                tmp = SYNTH_U32(tmp);
                
                pdw += 4;
                
                data = pdw + tmp;
                
                ssnd_ck_flag = 1;
                
                if (comm_ck_flag != 0) 
                {
                    return data;
                }
            }
            
            break;
        default:
            pdw += (ck_size + 1) & ~0x1;
        }
    }
    
    return data;
}
