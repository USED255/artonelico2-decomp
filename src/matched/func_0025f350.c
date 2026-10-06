
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
s32 func_00191760(s32, s32);
M2C_UNK func_0025ef64(void *);
M2C_UNK func_00270e6c(void *, M2C_UNK *);
M2C_UNK func_00278db8(s32, s32);
M2C_UNK func_002792c0(s32);
M2C_UNK func_0027939c(s32);
M2C_UNK func_002793f4(s32, s16, s32);
M2C_UNK func_00279528(s32, s32);
s32 func_0027954c(s32);
M2C_UNK func_0027955c(s32, M2C_UNK);
extern M2C_UNK D_0054AA00;
extern M2C_UNK D_009A17A8;
void func_0025f350(void *arg0)
{
  s32 temp_s0;
  s8 *new_var;
  s32 temp_s3;
  s32 temp_v0;
  s32 var_s0;
  temp_s3 = arg0 + 0x4E8;
  var_s0 = 0;
  func_0027939c(temp_s3);
  do
  {
    func_00279528(temp_s3, var_s0);
    var_s0 += 1;
  }
  while ((float) (var_s0 < 3));
  temp_s0 = arg0 + 0x1178;
  new_var = (s8 *) (&D_0054AA00);
  func_002793f4(temp_s3, *((s16 *) (new_var + 0x170)), (*((s16 *) (new_var + 0x172))) + 8);
  func_0027955c(temp_s3, 1);
  *((s8 *) (((s8 *) arg0) + 0x4EA)) = 0x10;
  *((u8 *) (((s8 *) arg0) + 0x4E9)) = (u8) (*((u8 *) (((s8 *) arg0) + 0x4EB)));
  *((s32 *) (((s8 *) arg0) + 0x1A1C)) = func_0027954c(temp_s3);
  func_0025ef64(arg0);
  temp_v0 = func_00191760(*((s32 *) (((s8 *) (((*((s16 *) (((s8 *) arg0) + 0xD26))) * 4) + arg0)) + 0x1920)), *((s32 *) (((s8 *) arg0) + 0x1A1C)));
  *((u32 *) (((s8 *) arg0) + 0x1A18)) = temp_v0;
  func_00278db8(temp_s0, temp_v0);
  func_002792c0(temp_s0);
  func_00270e6c(arg0 + 0x4D4, &D_009A17A8);
  *((s8 *) (((s8 *) arg0) + 0x4D6)) = 0x10;
  *((u8 *) (((s8 *) arg0) + 0x4D5)) = (u8) (*((u8 *) (((s8 *) arg0) + 0x4D7)));
}
