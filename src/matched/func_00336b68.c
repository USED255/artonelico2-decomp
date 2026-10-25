/* func_00336b68 @ 0x00336b68 (36 B) : call func_003369c0 and test the second stack slot */
extern void func_003369c0(int, int *);

int func_00336b68(int a)
{
  int buf[2];
  func_003369c0(a, buf);
  return buf[1] != 0;
}
