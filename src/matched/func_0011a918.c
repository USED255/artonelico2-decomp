/* func_0011a918 : tail wrapper forwarding scaled a2/a3 to func_0011a898 */
extern void func_0011a898(int, int, int, int);

void func_0011a918(int a0, int a1, int a2, int a3)
{
  func_0011a898(a0, a1, (a2 + 0x6C0) << 4, (a3 + 0x720) << 4);
}
