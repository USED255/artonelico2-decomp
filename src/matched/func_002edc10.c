/* func_002edc10 @ 0x002edc10 (40 B, CRI) : fill an 8-int buffer and return buf[1]+buf[3] */
extern void func_002ece68(int, int, int *);

int func_002edc10(int a, int b)
{
  int buf[8];
  func_002ece68(a, b, buf);
  return buf[1] + buf[3];
}
