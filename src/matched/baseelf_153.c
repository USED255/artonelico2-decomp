/* baseelf_153 : tail wrapper forwarding scaled a2/a3 to func_00115668 */
extern void func_00115668(int, int, int, int);

void baseelf_153(int a0, int a1, int a2, int a3)
{
  func_00115668(a0, a1, (a2 + 0x6C0) << 4, (a3 + 0x720) << 4);
}
