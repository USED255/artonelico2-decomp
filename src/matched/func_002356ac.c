
typedef signed char s8;
typedef unsigned char u8;
typedef short s16;
typedef unsigned short u16;
typedef int s32;
typedef unsigned int u32;
typedef long long s64;
typedef unsigned long long u64;
typedef float f32;
typedef double f64;
typedef unsigned char undefined1;
typedef unsigned short undefined2;
typedef unsigned int undefined4;
typedef unsigned long long undefined8;
typedef unsigned char byte;
typedef unsigned char code;
typedef unsigned int uint;
typedef int s128;
typedef int u128;
typedef int s64_;
extern unsigned char *sp;
typedef s32 M2C_UNK;
typedef s8 M2C_UNK8;
typedef s16 M2C_UNK16;
typedef s32 M2C_UNK32;
typedef s64 M2C_UNK64;
extern M2C_UNK D_00BFEAA8;
void func_002356ac(s32 arg0)
{
  s32 temp_t6;
  s8 *new_var2;
  M2C_UNK *new_var;
 do { new_var2 = (s8 *) (&D_00BFEAA8); temp_t6 = (*((u16 *) (new_var2 + 2))) + arg0; if (temp_t6 < (0xFFFE + 1)) { new_var = &D_00BFEAA8; do { *((u16 *) (((s8 *) new_var) + 2)) = (u16) temp_t6; } while (0); } } while (0);
}
