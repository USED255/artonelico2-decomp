/* func_00114890 : tail wrapper forwarding scaled a2/a3 to func_00113e8c */
extern void func_00113e8c(int, int, int, int);

void func_00114890(int a0, int a1, int a2, int a3)
{
  func_00113e8c(a0, a1, (a2 + 0x6C0) << 4, (a3 + 0x720) << 4);
}
