/* func_002edbe8 @ 0x002edbe8 (40 B, CRI) : fill an 8-int buffer and return buf[1]+buf[3] */
extern void func_002ece80(int, int, int *);

int func_002edbe8(int a, int b)
{
  int buf[8];
  func_002ece80(a, b, buf);
  return buf[1] + buf[3];
}
