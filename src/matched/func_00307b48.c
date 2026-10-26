/* func_00307b48 @ 0x00307b48 (36 B, CRI) : clear the word returned by func_00307b70, then tail-call func_00307b80(0x80) */
extern int *func_00307b70(void);
extern void func_00307b80(int);

void func_00307b48(void)
{
  int *p = func_00307b70();
  *p = 0;
  func_00307b80(0x80);
}
