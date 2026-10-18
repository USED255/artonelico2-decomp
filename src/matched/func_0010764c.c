typedef unsigned char u8;
typedef struct { u8 pad[0x1C]; u8 b[0x12]; } S_A505C0;
extern S_A505C0 D_00A505C0;
void func_0010764c(u8 *dst)
{
  int i;
  for (i = 0; i < 0x12; i++) dst[i] = D_00A505C0.b[i];
}
